#__author:  Administrator
#date:  2017/2/15
import socket


for k in range(10):
    client = socket.socket()
    client.setblocking(False)
    try:
        client.connect(('64.233.188.138',80,))
    except Exception as e:
        print(e)

while True:
    print('等待...')
