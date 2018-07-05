from django.shortcuts import render
from  django.http import HttpResponse
# Create your views here.


def index(req):
    return render(req, 'index.html')

def index_post(req):
    return render(req, 'index_post.html')

def ajax_receive(req):
    print(req.method)
    if req.method == "POST":
        print(req.POST)
    return HttpResponse("http ok")

def index_jq(req):
    return render(req, 'index_jq.html')

def ajax_receive_jquery(req):
    if req.method == "POST":
        print(req.POST)
    else:
        print(req.GET)
    return HttpResponse("jquery ajax")
