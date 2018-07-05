from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate

def login(req):
    message = ""

    if req.method == "POST":
        user = req.POST.get('user')
        pwd = req.POST.get('pwd')
        user_auth = authenticate(username=user, password=pwd)

        if user_auth is not None:
            # the password verified for the user
            req.session['is_login'] = True
            req.session['username'] = user
            next_jp = req.POST.get('next','/')

            return redirect(next_jp)
        else:
            # the authentication system was unable to verify the username and password
            message = "用户与密码输入错误."
            obj = render(req,'auth/login.html', {'msg': message})
            
            return obj

    return render(req,'auth/login.html', {'msg': message, "cur_user": getCurUser(req), "next":req.GET.get('next','/')})

def logout(req):
    req.session.clear()
    return redirect('/')

def auth(func):
    def inner(req, *args, **kwargs):
        is_login = req.session.get('is_login')
        if is_login:
            return func(req, *args, **kwargs)
        else:
            return redirect('/login/?next='+req.path)
    return inner

def getCurUser(req):
    is_login = req.session.get('is_login',False)
    if not is_login:
        return "游客"
    return req.session.get('username',"游客")

