#__author:  Administrator
#date:  2016/12/29
from django.shortcuts import render
from django import forms
from app01 import models

class UserModelForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = "__all__"


def index(request):
    if request.method == "GET":
        obj = UserModelForm()
        return render(request,'mf.html',{'obj': obj})
    elif request.method == "POST":
        obj = UserModelForm(request.POST)
        if obj.is_valid():
            # print(obj.cleaned_data)
            # models.User.objects.create(**obj.cleaned_data)
            obj.save(commit=True)
            """
            mobj = obj.save(commit=False)
            mobj.save()
            obj.save_m2m()
            """
        print(obj.errors)
        return render(request, 'mf.html', {'obj': obj})

def edit_index(request,nid):
    if request.method == "GET":
        model_obj = models.User.objects.get(id=nid)
        obj =UserModelForm(instance=model_obj)
        return render(request, 'mf1.html', {'obj': obj,'nid': nid})
    elif request.method == 'POST':
        model_obj = models.User.objects.get(id=nid)

        obj = UserModelForm(request.POST, instance=model_obj)
        if obj.is_valid():
            obj.save()
        return render(request, 'mf1.html', {'obj': obj})


