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
from django.conf.urls import url
from View import views,views_auth,views_paper,views_bom,views_product
urlpatterns = [
    url(r'^$',views.index),  
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    
    path('product/', views_product.product, name='product'),
    path('product/add/', views_product.product_add, name='product_add'),
    path('product/edit/', views_product.product_edit, name='product_edit'),  
    path('product/update/', views_product.product_update, name='product_update'),  
    
    path('bom/', views_bom.bom, name='bom'),
    path('bom/detail/', views_bom.bom_detail, name='bom_detail'),
    path('bom/update/', views_bom.bom_update, name='bom_update'),  
    path('bom/add/', views_bom.bom_add, name='bom_add'),  
    path('bom/edit/', views_bom.bom_edit, name='bom_edit'),
    path('bom/clone/', views_bom.bom_clone, name='bom_clone'),  
      
    path('paper/', views_paper.paper, name='paper'),
    path('paper/search/', views_paper.paper_search, name='paper_search'),
    path('paper/update/', views_paper.paper_update, name='paper_update'),  
    path('paper/add/', views_paper.paper_add, name='paper_add'),
    path('paper/edit/', views_paper.paper_edit, name='paper_edit'),  
    
    path('login/', views_auth.login, name='login'),
    path('logout/', views_auth.logout, name='logout'),
    
    path('history/', views.history, name='history'),  
]
