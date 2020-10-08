from database import UserData
import socket
import sys
import os
import threading
import argparse

#### arg parse 
#### run by using puthon3 server.py <host> <port>
host = "127.0.0.1"      #default host
port = 49155            #default port
argp = argparse.ArgumentParser()
argp.add_argument("host")
argp.add_argument("port")
args = argp.parse_args()
host = str(args.host)
port = int(args.port)
print(f"Server host: {host}, port: {port}")


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

    def run(self):
        welcome_message = "********************************\n** Welcome to the BBS server. **\n********************************"
        self.client.send(welcome_message.encode())
        try:
            while True:
                self.client.send("% ".encode())
                print("Waiting for cmd")
                cmd = self.client.recv(1024).decode()
                print("From "+str(self.address)+" received message : "+cmd)
                response = self.response(cmd, self.client)
                self.client.send(response.encode())
                if response == "exit":
                    self.client.close()
                    break
        except ConnectionResetError:
            print(f"Client {str(self.address)} shut down unexceptedly.")
            self.client.close()

    def response(self, cmd, client):
        if cmd == "":
            return "400 Error Bad request!"
        cmd = cmd.split(" ")
        if  len(cmd) == 0:
            return f"Unable to recognize {str(len(cmd))}"
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
        elif cmd[0] == "login":
            # try:
            username = cmd[1]
            password = cmd[2]
            check = self.db.find_username(username)
            if self.username != "":
                return "Please logout first."
            elif password == check[2]:
                self.username = username
                self.password = password
                return f"Welcome, {self.username}"
            else:
                return "Login failed."
            # except:
                # return "Usage: login <username> <password>"
        elif cmd[0] == "logout":
            if self.username == "":
                return "Please login first."
            else:
                username = self.username
                self.username = ""
                self.email = ""
                self.password = ""
                return f"Bye, {username}"
        elif cmd[0] == "whoami":
            if self.username != "":
                return f"{self.username}"
            else :
                return "Please login first."
        elif cmd[0] == "list-user":
            data = self.db.print()
            ret = "Name        Email\n"
            for item in data:
                ret += item[0]+"      "+item[1]+"\n"
            return ret
        elif cmd[0] == "exit":
            return "exit"
        else:
            print(f"cannt catch cmd {cmd}")
        return "What?"


def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(20)
    print("Server start to run.")
    while True:
        client, addr = s.accept()
        BBS_sever(client, addr).start()

if __name__ == "__main__":
    main()
