# -*-: coding:utf-8 -*-
from django.shortcuts import render
from View import views_auth
from View import models
from django.http import HttpResponse
# Create your views here.
def index(req):
    return render(req,"index.html", {"cur_user": views_auth.getCurUser(req)})

class ErrorInfo(object):
    exists_error   = "添加失败，请检查输入是否有误，或者已存在相同的记录！"
    nochange_error = "未做任何修改！"
    update_error   = "更新失败，请检查输入是否有误，或者已存在相同的记录！" 
    no_exists_bom  = "无法找到Bom信息！"
    data_error     = "数据错误！"    
    
def history(req):
    result = []
    
    if req.method == "GET":
        tableName = req.GET.get("table")
        recordId = req.GET.get("id")

        if tableName and recordId:
            result = models.DataHistory.objects.filter(tableName=tableName, recordId=recordId)
    return render(req,"history.html", {"history":result, "cur_user": views_auth.getCurUser(req)})

        
        