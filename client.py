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


udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udpserver.connect((host,port))
print("UDP Server connect success")



server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Start to connect")
server.connect((host,port))
print("Connected Success")
print(server.recv(1024).decode())

rannum = str()

while True :
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
    else :
        server.send(cmd.encode())
        response = server.recv(1024).decode()
        if "login" in cmd:
            response = response.split("$")
            if len(response) > 1:
                rannum = response[1]
            response = response[0]
        if response == "exit":
            server.close()
            break
        print(response)

