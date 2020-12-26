#!/usr/bin/env python3

import socket
import argparse
import threading
import time
from datetime import datetime
#### arg parse 
#### run by using puthon3 client.py <host> <port>
host = "127.0.0.1"  #default host
port = 7890         #default port
argp = argparse.ArgumentParser()
argp.add_argument("host")
argp.add_argument("port")
args = argp.parse_args()
host = str(args.host)
port = int(args.port)



udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udpserver.connect((host,port))

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.connect((host,port))
print(server.recv(1024).decode())

rannum = ""
chatter = list()
history = list()
attach = False
server_running = False
server_running_joinother = False
chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
chatroom_addr = str()
chatroom_port = int()
myname = str()

def get_time():
    today = datetime.now()
    res = today.strftime("%H:%M")
    return res

class chatroom_server(threading.Thread):
    def __init__(self,client,address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
    def run(self):
        global attach,server_running
        try:
            welcome_message = "***************************\n**Welcome to the chatroom**\n***************************"
            for it in history:
                welcome_message += "\n"+it
            self.client.send(welcome_message.encode())
            while server_running == True:
                message = self.client.recv(1024).decode()
                # print(f"receive: {message}")
                if "leave-chatroom" in message:
                    break
                if "sys" not in message and message != "":
                    history.append(message)
                while len(history) > 3:
                    history.pop(0)
                if myname in message and "leave us" in message:
                    self.client.close()
                    break
                for client in chatter:
                    if client == self.client:
                        continue
                    else:
                        client.send(message.encode())
                if "leave us." in message:
                    self.client.close()
                    break
                if "the chatroom is close" in message:
                    attach = False
                    server_running = False
                    break
        except BrokenPipeError:
            pass
        try:
            chatter.remove(self.client)
        except:
            pass
class chatroom_server_set_up(threading.Thread):
    def __init__(self,address,port):
            threading.Thread.__init__(self)
            self.host = address
            self.port = int(port)
    def run(self):
            chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            chatroom.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            try:
                chatroom.bind((self.host, self.port))
            except OSError:
                pass
            chatroom.listen(20)
            while server_running == True:
                client, addr = chatroom.accept()
                chatroom_server(client,addr).start()
                chatter.append(client)
            chatroom.close()

class chatroom_listen(threading.Thread):
    def __init__(self,chatroom_server):
        threading.Thread.__init__(self)
        self.chatroom_server = chatroom_server
    def run(self):
        global attach
        global chatroom
        while attach == True:
            try:
                response = self.chatroom_server.recv(1024).decode()
                if attach == False:
                    break
                if response != "":
                    print(response)
                if "the chatroom is close" in response:
                    print("Welcome back to BBS.")
                    attach = False
                    chatroom.close()
                    chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    break
            except:
                break

while True :
    if attach == False:
        print("% ",end="")
    cmd = input()
    if attach == False:
        if "attach" == cmd:
            if rannum == "":
                print("Please login first.")
            if server_running == False:
                if len(history) == 0:
                    print("Please create-chatroom first.")
                else:
                    print("Please restart-chatroom first.")
            attach = True
            chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            chatroom.connect((chatroom_addr,chatroom_port))
            chatroom_listen(chatroom).start()
        elif "register" in cmd or "whoami" in cmd:
            if "whoami" in cmd:
                cmd = cmd + f" {rannum}"
            udpserver.sendto(cmd.encode(),(host,port))
            response,address = udpserver.recvfrom(1024)
            response = response.decode()
            print(response)
        else :
            server.send(cmd.encode())
            response = server.recv(1024).decode()
            if "login" in cmd:
                myname = cmd.split(" ")[1]
                response = response.split("$")
                if len(response) > 1:
                    rannum = response[1]
                response = response[0]
            elif response == "exit":
                server.close()
                break
            elif "start to create chatroom" in response:
                attach = True
                chatroom_addr = response.split(" ")[4]
                chatroom_port = int(response.split(" ")[5])
                chatroom_server_set_up(chatroom_addr,chatroom_port).start()
                server_running = True
                time.sleep(0.1)
                chatroom.connect((chatroom_addr,chatroom_port))
                chatroom_listen(chatroom).start()
                continue
            elif "Action: connection to chatroom server." in response:
                if server_running == True:
                    server_running_joinother = True
                attach = True
                chatroom.connect((response.split()[5],int(response.split()[6])))
                chatroom_listen(chatroom).start()
                chatroom.send(f"sys [{get_time()}] : {myname} join us.".encode())
                continue
            print(response)
    else:
        try:
            if "detach" == cmd and server_running == True:
                print("Welcome back to BBS.")
                chatroom.send(f"sys [{get_time()}] : {myname} leave us.".encode())
                chatroom.close()
                chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                attach = False
            elif "leave-chatroom" == cmd:
                # print(f"{server_running} , {server_running_joinother}")
                if server_running == True and server_running_joinother == False:
                    server.send(cmd.encode())
                    response = server.recv(1024).decode()
                    # print(f"doing shutdown server chatroom process")
                    chatroom.send(f"sys [{get_time()}] : the chatroom is close".encode())
                    chatroom.close()
                    chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    chatter = list()
                    server_running = False
                else:
                    if server_running == True and server_running_joinother == False:
                        pass
                    else:
                        chatroom.send(f"sys [{get_time()}] : {myname} leave us.".encode())
                    chatroom.close()
                    chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                server_running_joinother = False
                attach = False
                print("Welcome back to BBS.")
            else:
                cmd = f"{myname}[{get_time()}]: {cmd}"
                # print(f"check send mes {cmd}")
                chatroom.send(cmd.encode())
        except BrokenPipeError:
            attach = False
        