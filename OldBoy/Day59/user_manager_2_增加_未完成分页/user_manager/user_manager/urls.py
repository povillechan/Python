"""user_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^login.html$', views.login),
    url(r'^login.html$', views.Login.as_view()),
    url(r'^logout.html$', views.logout),
    url(r'^index.html$', views.index),
    url(r'^classes.html$', views.handle_classes),
    url(r'^add_classes.html$', views.handle_add_classes),
    url(r'^student.html$', views.handle_student),
    url(r'^teacher.html$', views.handle_teacher),
    # url(r'^test.html$', views.test),
    # url(r'^xiaohu.html$', views.xiaohu),
    # url(r'^js_cookie.html$', views.js_cookie),
]
