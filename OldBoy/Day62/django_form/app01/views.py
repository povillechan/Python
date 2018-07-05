from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse

from django import forms
# 模版
class LoginForm(forms.Form):
    # 模版中的元素
    user = forms.CharField(min_length=6,error_messages={"required": '用户名不能为空','min_length': '用户名长度不能小6'})
    email = forms.EmailField(error_messages={"required": '邮箱不能为空','invalid': '邮箱格式错误'})

class IndexForm(forms.Form):
    # 模版中的元素
    user = forms.CharField(min_length=6,error_messages={"required": '用户名不能为空','min_length': '用户名长度不能小6'})
    email = forms.EmailField(error_messages={"required": '邮箱不能为空','invalid': '邮箱格式错误'})
    favor = forms.MultipleChoiceField(
        choices=[(1,'小虎'),(2,'小小虎'),(3,'小B虎')]
    )

import json
from datetime import date
from datetime import datetime

def index(request):
    obj = IndexForm()
    return render(request,'index.html',{'obj': obj})

def edit_index(request):
    obj = IndexForm({'user': 'root','email': 'root@live.com','favor': [2,3]})
    return render(request,'index.html',{'obj': obj})


def login(request):
    if request.method == "GET":
        # 数据库中获取
        obj = LoginForm()
        return render(request,'login.html',{'oo': obj})
    elif request.method == "POST":
        """
        obj = LoginForm(request.POST)
        # 验证
        status = obj.is_valid()
        print(status)

        value_dict = obj.clean()
        print(value_dict)

        error_obj = obj.errors.as_json()
        print(error_obj)
        """
        obj = LoginForm(request.POST)
        if obj.is_valid():
            value_dict = obj.clean()
            print(value_dict)
            # create(**value_dict)
        else:
            # 封装了所有的错误信息
            # print(obj.errors['email'][0])
            # print(obj.errors["user"][0])
            # print(type(error_obj))
            from django.forms.utils import ErrorDict
            pass

        return render(request, 'login.html',{'oo': obj})


def login_ajax(request):
    if request.method == "GET":
        return render(request, 'login_ajax.html')
    elif request.method == "POST":
        ret = {'status': True, 'error':None, 'data': None}
        obj = LoginForm(request.POST)
        if obj.is_valid():
            print(obj.clean())
        else:
            # 方式一
            # res_str = obj.errors.as_json() # res_str是一个字符串
            # ret['status'] = False
            # ret['error'] = res_str
            # 两次反序列化
            # 方式二：
            ret['status'] = False
            ret['error'] = obj.errors.as_data() # # {'user': [ValidationError(['用户名长度不能小6'])], 'email': [ValidationError(['邮箱格式错误'])]}
            # # 一次反序列化
        return HttpResponse(json.dumps(ret,cls=JsonCustomEncoder))

from django.core.validators import ValidationError
class JsonCustomEncoder(json.JSONEncoder):
    def default(self, field):
        if isinstance(field, ValidationError):
            return {'code': field.code, 'message': field.message}
        else:
            return json.JSONEncoder.default(self, field)
"""
def login(request):
    if request.method == "GET":
        return render(request,'login.html')
    elif request.method == "POST":
        # 不爽
        u = request.POST.get('user')
        e = request.POST.get('email')
        p = request.POST.get('pwd')
        # 判断用户输入是否为空，提示用户那个错误
        # ...
        # 判断某种格式是否正确,提示用户那个错误
        # ..
        # 数据库校验：
        # filter(user=u,email=e,pwd=p) # filter(**{})
        # create(user=u,email=e,pwd=p) # create(**{})
        # 只要上述条件有一个不满足，

        # 页面上一次提交的数据，无法保留（Form提交）
        return render(request,'login.html', {})
        # return redirect('/login.html')
"""