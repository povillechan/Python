# -*- coding:utf-8 -*-
'''
Created on 2018-4-19

@author: povil
'''

import socketserver

class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
#        socketserver.BaseRequestHandler.handle(self)
        conn =self.request
        conn.sendall(bytes('Welcome 10086', 'utf-8'))
        Flag = True
        while Flag:
            data = str(conn.recv(1024), 'utf-8')
            if data == 'exit':
                Flag = False
            elif data == '0' :
                conn.sendall(bytes('手机业务', 'utf-8'))
            elif data == '1':
                conn.sendall(bytes('宽带业务', 'utf-8'))
            else:
                conn.sendall(bytes('重新输入', 'utf-8'))
        
        
if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1', 9000), MyServer)
    server.serve_forever()
        
