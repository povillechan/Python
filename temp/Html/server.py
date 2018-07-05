'''
@author: chenzf

'''

import socket
from _socket import SOCK_STREAM

def main():
    sock = socket.socket(socket.AF_INET, SOCK_STREAM)
    sock.bind(('localhost', 14000))
    sock.listen(3)
    
    while True:
        conn,address = sock.accept()
        buf = conn.recv(1024)
        print(buf.decode("utf8"))
        
        conn.sendall("<h1>Hello World</h1>")
        conn.close()       


if __name__ ==  '__main__':
    main()