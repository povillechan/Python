from django.shortcuts import render,HttpResponse
from django import forms

forms.Form
# Create your views here.

def test(request):
    print(request.method)
    print(request.GET)
    print(request.POST)
    print(request.body)
    return HttpResponse('..')