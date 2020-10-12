from database import UserData
import socket
import sys
import os
import threading
import argparse
import random

#### arg parse 
#### run by using puthon3 server.py <host> <port>
host = "127.0.0.1"      #default host
port = 49155            #default port
argp = argparse.ArgumentParser()
argp.add_argument("port")
args = argp.parse_args()
port = int(args.port)
print(f"Server host: {host}, port: {port}")

#### radom generate num
randomdict = dict()



class BBS_sever(threading.Thread):
    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        print(f"New connection {self.address}")
        self.db = UserData()
        self.username = ""
        self.email = ""
        self.password = ""
        self.rannum = ""

    def run(self):
        welcome_message = "********************************\n** Welcome to the BBS server. **\n********************************"
        self.client.send(welcome_message.encode())
        try:
            while True:
                cmd = self.client.recv(1024).decode()
                print("From "+str(self.address)+" received message : "+cmd)
                response = self.response(cmd, self.client)
                self.client.send(response.encode())
                if response == "exit":
                    self.client.close()
                    break
        except (ConnectionResetError,ConnectionAbortedError,BrokenPipeError):
            print(f"Client {str(self.address)} shut down unexceptedly.")
            self.client.close()

    def response(self, cmd, client):
        if cmd == "":
            return "400 Error Bad request!"
        cmd = cmd.split(" ")
        if  len(cmd) == 0:
            return f"Unable to recognize {str(len(cmd))}"
        elif cmd[0] == "login":
            try:
                username = cmd[1]
                password = cmd[2]
            except:
                return "Usage: login <username> <password>"

            check = self.db.find_username(username)
            if self.username != "":
                return "Please logout first."
            elif check is not None and  password == check[2]:
                self.username = username
                self.password = password
                self.rannum = self.insert_randomlist(username)
                return f"Welcome, {self.username}${self.rannum}"
            else:
                return "Login failed."

        elif cmd[0] == "logout":
            if self.username == "":
                return "Please login first."
            else:
                username = self.username
                self.username = ""
                self.email = ""
                self.password = ""
                randomdict.pop(self.rannum, None)
                self.rannum = ""
                return f"Bye, {username}"
        elif cmd[0] == "list-user":
            data = self.db.print()
            ret = "{:<12s}{:<12s}".format("Name","Email")+"\n"
            for item in data:
                ret += "{:<12s}{:<12s}".format(item[0],item[1])+"\n"
            return ret
        elif cmd[0] == "exit":
            return "exit"
        else:
            print(f"can not handle cmd {cmd}")
        return "What?"
    def insert_randomlist(self,username):
        rannum = str(random.random())
        while randomdict.get(rannum) != None:
            rannum = str(random.random())
        randomdict[rannum] = username
        return rannum

class UDP_server(threading.Thread):
    def __init__(self,host,port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.db = UserData()
    def run(self):
        while True:
            cmd,address = self.s.recvfrom(1024)
            cmd = cmd.decode()
            print(f"form {address}: {cmd}")
            self.s.sendto(self.response(cmd).encode(),address)
    def response(self,cmd):
        cmd = cmd.split(" ")
        if len(cmd) == 0:
            return "Bad request"
        elif cmd[0] == "register":
            try:
                username = cmd[1]
                email = cmd[2]
                password = cmd[3]
                if self.db.create_new_user(username,email,password) is True:
                    return "Register successfully."
                else:
                    return "Username is already used."
            except:
                return "Usage: register <username> <email> <password>"
        elif cmd[0] == "whoami":
            if len(cmd) < 2:
                return "error!"
            rannum = cmd[1]
            if randomdict.get(rannum) != None:
                return randomdict[rannum]
            else :
                return "Please login first."
        return "UDP WHAT!"+str(cmd)
                




def main():
    UDP_server(host,port).start()

    # print("UDP Server ready.")
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((host, port))
    s.listen(20)
    # print("TCP Server start to run.")
    print("Server ready.")

    while True:
        client, addr = s.accept()
        BBS_sever(client, addr).start()

if __name__ == "__main__":
    main()
