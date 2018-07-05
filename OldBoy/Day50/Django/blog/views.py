from django.shortcuts import render, render_to_response
from blog import models
from  django.http import HttpResponse
# Create your views here.
import datetime

# user_list = []


def cur_time(request):
    cur_time_t = datetime.datetime.now()
    return render(request, "cur_time.html", {"cur_time":cur_time_t})


def userinfo(request):    
    if request.method == "POST":
        username = request.POST.get("username", None)
        sex = request.POST.get("sex", None)
        email = request.POST.get("email", None)
       
#         print(username)
#         print(sex)
#         print(email)
#         user = {"username":username, "sex":sex, "email": email}
#         user_list.append(user)

        models.UserInfo.objects.create(
            username=username,
            sex=sex,
            email=email,
            )
        
        user_list= models.UserInfo.objects.all()
        
        user_names = models.UserInfo.object.filter(username="dd").Values("sex")
        return render(request, "userinfo.html", {"user_list":user_list})
    else:
        print("haha")
       
    return render(request, "userinfo.html")


def special_case(request, year, month):    
    
    return HttpResponse("year: "+year+" month: " + month)
#     return render_to_response(template_name, context, content_type, status, using)
