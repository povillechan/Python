"""ZSY_BOM_MAN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import  url
from View import views,auth
urlpatterns = [
    url(r'^$',views.index),  
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    
    path('product/', views.product, name='product'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/edit/', views.product_edit, name='product_edit'),  
    path('product/update/', views.product_update, name='product_update'),  
    
    path('bom/', views.bom, name='bom'),
    path('bom/detail/', views.bom_detail, name='bom_detail'),
    path('bom/update/', views.bom_update, name='bom_update'),  
    path('bom/add/', views.bom_add, name='bom_add'),  
    path('bom/edit/', views.bom_edit, name='bom_edit'),
    path('bom/clone/', views.bom_clone, name='bom_clone'),  
      
    path('paper/', views.paper, name='paper'),
    path('paper/search/', views.paper_search, name='paper_search'),
    path('paper/update/', views.paper_update, name='paper_update'),  
    path('paper/add/', views.paper_add, name='paper_add'),
    path('paper/edit/', views.paper_edit, name='paper_edit'),  
    
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
]
