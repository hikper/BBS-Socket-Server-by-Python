import socket
import argparse

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




s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Start to connect")
s.connect((host,port))
print("Connected Success")
print(s.recv(1024).decode())

while True :
    print(s.recv(1024).decode(),end="")
    cmd = input()
    while len(cmd) == 0:
        cmd = input()
    s.send(cmd.encode())
    response = s.recv(1024).decode()
    print(response)
    if response == "exit":
        print("Exit.")
        s.close()
        break

