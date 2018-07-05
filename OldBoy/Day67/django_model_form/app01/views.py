from django.shortcuts import render,HttpResponse
from app01 import models

def index(request):
    # obj = models.News.objects.get(id=1)
    # v = obj.favor.all()
    # print(v)
    # obj.favor.add(1)
    # obj.favor.remove(1)
    # v = obj.favor.all()
    # obj.favor.clear()
    # v = models.User.objects.all()
    # v = models.User.objects.all().select_related('user_type')
    v = models.User.objects.all().prefetch_related('user_type')
    return render(request,'index.html',{'v': v})