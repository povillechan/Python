
default_headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}


def download(headers = None):
    if headers:
        new_headers = default_headers.copy()
        new_headers.update(headers)
        print(type(headers))
        print(default_headers.copy())
        print(new_headers)
    else:
        print(default_headers)
        
        
download(headers={'2':'2'})
        


        