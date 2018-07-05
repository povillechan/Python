'''
Created on 2018-4-19

@author: povil
'''
import socket

ip_port = ('127.0.0.1',9000)
sk = socket.socket()
sk.connect(ip_port)
sk.settimeout(5)

while True:
    data = sk.recv(1024)
    print('receive:',str(data, 'utf-8'))
    inp = input('please input:')
    sk.sendall(bytes(inp, 'utf-8'))
    if inp == 'exit':
        break

sk.close()