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
print(f"Server host: {host}, port: {port}")


udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udpserver.connect((host,port))
print("UDP Server connect success")



server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Start to connect")
server.connect((host,port))
print("Connected Success")
print(server.recv(1024).decode())

rannum = ""

chatter = list()
history = list()

attach = False
server_running = False
chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


class chatroom_server(threading.Thread):
    def __init__(self,client,address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
    def run(self):
        welcome_message = "***************************\n**Welcome to the chatroom**\n***************************"
        for it in history:
            welcome_message += "\n"+it
        self.client.send(welcome_message.encode())
        # print(f"server is runnung here!")
        while server_running == True:
            message = self.client.recv(1024).decode()
            # print(f"receive mes! {message}")
            if "leave-chatroom" in message:
                break
            if "sys" not in message:
                history.append(message)
            while len(history) > 3:
                history.pop(0)
            for client in chatter:
                if client == self.client:
                    # print(f"myself")
                    continue
                else:
                    # print(f"not myself {message}")
                    client.send(message.encode())
            if "leave us." in message:
                chatter.remove(self.client)
                self.client.close()
                break

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
                asdasdasd = int()
            chatroom.listen(20)
            # print("chatroom_server_ready")
            while server_running == True:
                client, addr = chatroom.accept()
                chatroom_server(client,addr).start()
                # client.send("wewewewe".encode())
                chatter.append(client)

class chatroom_listen(threading.Thread):
    def __init__(self,chatroom_server):
        threading.Thread.__init__(self)
        self.chatroom_server = chatroom_server
    def run(self):
        global attach
        global chatroom
        while attach == True:
            response = self.chatroom_server.recv(1024).decode()
            if response != "":
                print(response)
            if "the chatroom is close" in response:
                attach = False
                chatroom.close()
                chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                break
        # print(f"lister is end!!!")





        






myname = str()
while True :
    if attach == False:
        cmd = input("% ")
        while len(cmd) == 0:
            cmd = input()
        if "register" in cmd or "whoami" in cmd:
            if "whoami" in cmd:
                cmd = cmd + f" {rannum}"
            udpserver.sendto(cmd.encode(),(host,port))
            response,address = udpserver.recvfrom(1024)
            response = response.decode()
            print(response)
        if "attach" in cmd:
            if rannum == "":
                print("Please login first.")
            if server_running == False:
                print("Please create-chatroom first.")
            print("***************************\n**Welcome to the chatroom**\n***************************")
            for item in history:
                print(item)
            attach = True
        else :
            server.send(cmd.encode())
            response = server.recv(1024).decode()
            if "login" in cmd:
                myname = cmd.split(" ")[1]
                response = response.split("$")
                if len(response) > 1:
                    rannum = response[1]
                response = response[0]
            if response == "exit":
                server.close()
                break
            if "start to create chatroom" in response:
                attach = True
                chatroom_addr = response.split(" ")[4]
                chatroom_port = int(response.split(" ")[5])
                # print("start to create chatroom…")
                chatroom_server_set_up(chatroom_addr,chatroom_port).start()
                server_running = True
                time.sleep(1)
                chatroom.connect((chatroom_addr,chatroom_port))
                chatroom_listen(chatroom).start()
                continue
            if "Action: connection to chatroom server." in response:
                print("Action: connection to chatroom server")
                attach = True
                chatroom.connect((response.split()[5],int(response.split()[6])))
                chatroom_listen(chatroom).start()
                today = datetime.now()
                res = today.strftime("%H:%M")
                chatroom.send(f"sys [{res}] : {myname} join us.".encode())
                
                continue

            print(response)
    else:
        try:
            cmd = input("")
            today = datetime.now()
            res = today.strftime("%H:%M")
            if "detach" in cmd and server_running == True:
                print("Welcome back to BBS.")
                attach = False
            elif "leave-chatroom" in cmd:
                if server_running == True:
                    server.send(cmd.encode())
                    response = server.recv(1024).decode()
                    chatroom.send(f"sys[{res}] : the chatroom is close".encode())
                    chatroom.close()
                    chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    chatter = list()
                else:
                    chatroom.send(f"sys [{res}] : {myname} leave us.".encode())
                    chatroom.close()
                    chatroom = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                server_running = False
                attach = False
            else:
                cmd = f"{myname}[{res}]: {cmd}"
                # print(f"check send mes {cmd}")
                chatroom.send(cmd.encode())
        except BrokenPipeError:
            print("Chatroom connection has beeen lost")
        