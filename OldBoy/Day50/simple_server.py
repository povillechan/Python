'''

@author: chenzf
'''
from wsgiref.simple_server import make_server

def application(environ, start_response):
#     print(environ)

    start_response('200 OK', [('Content-Type', 'text/html')])
   
    path=environ["PATH_INFO"]
    print(path)
    if path=="/book":
        return [b'<h1>Hello, book!</h1>']
    elif path=="/web":
        return [b'<h1>Hello, Web!</h1>']
    else:
        return [b'<h1>Hello, World!</h1>']


if __name__ == "__main__":
    httpd = make_server('', 8010, application)
    httpd.serve_forever()