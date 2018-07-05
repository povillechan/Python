# -*-: coding:utf-8 -*-
from django.shortcuts import render
from View import models,views_auth,views
from django.http import HttpResponse
import json

# Create your views here.        
def bom(req):
    bom_table = models.Bom.objects.all().order_by("bomName")    
    return render(req,"bom/bom_list.html", {"bom_list":bom_table, "table":models.Bom._meta.verbose_name,"cur_user": views_auth.getCurUser(req)})

def bom_detail(req):
    if req.method == "GET":
        record_id = req.GET.get("id",None)
        bomName= req.GET.get("bomName",None)
        bomVersion= req.GET.get("bomVersion",None)
        bom = None
        if record_id:
            bom = models.Bom.objects.filter(id=record_id)
            if bom.exists():
                return render(req,"bom/bom_detail.html", {"bom":bom[0], "bom_list":json.dumps(bom[0].bomContext), "cur_user": views_auth.getCurUser(req)})
        elif bomName and bomVersion:
#            print(bomName, bomVersion)
            bom = models.Bom.objects.filter(bomName=bomName,bomVersion=bomVersion)
            if bom.exists():
                return render(req,"bom/bom_detail.html", {"bom":bom[0], "bom_list":json.dumps(bom[0].bomContext), "cur_user": views_auth.getCurUser(req)})
        return HttpResponse(views.ErrorInfo.no_exists_bom)
    
@views_auth.auth
def bom_update(req):
    if req.method == "GET":
        record_id = req.GET.get("id", None)
 
        if not record_id:
            return HttpResponse("无法找到Bom信息")
        
        bom = models.Bom.objects.filter(id=record_id)
        if bom.exists():
            return render(req,"bom/bom_update.html", {"bom":bom[0], "bom_Context":json.dumps(bom[0].bomContext),"cur_user": views_auth.getCurUser(req)})
            
    return HttpResponse("无法找到Bom信息")

@views_auth.auth
def bom_add(req):
    return render(req,"bom/bom_add.html", {"cur_user": views_auth.getCurUser(req)})  

@views_auth.auth
def bom_clone(req):
    if req.method == "GET":
        bomName = req.GET.get("bomName",None)
        bomVersion = req.GET.get("bomVersion", None)
 
        if not bomName or not bomVersion:
            return HttpResponse("无法找到Bom信息")
        
        bom = models.Bom.objects.filter(bomName=bomName, bomVersion=bomVersion)
        if bom.exists():
            return render(req,"bom/bom_add.html", {"bomName":bomName, "bomVersion":bomVersion, "bom_list":json.dumps(bom[0].bomContext), "bom_action":"clone","cur_user": views_auth.getCurUser(req)})
            
    return HttpResponse("无法找到Bom信息")

def bom_edit(req):
    response_dict = {'status': True, 'error': None, 'data': None}
    is_login = req.session.get('is_login')
    if not is_login:
        response_dict['status'] = False
        response_dict['error'] = "errLogin"
        response_dict['data'] = "?next="+req.path
 
        return HttpResponse(json.dumps(response_dict))
       
    if req.method == "POST":   
        action = req.POST.get('action')
        if action.lower() == "delete":
            record_id=req.POST.get('id', None)
            if record_id:
                data_item = models.Bom.objects.filter(id=record_id)[0]

                models.DataBaseLog.objects.create(
                    log_user   =   views_auth.getCurUser(req),
                    log_table  =   models.Bom._meta.verbose_name,
                    log_action =   "delete %s" %(str(data_item))
                )
          
                # 变更为删除状态
                models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Bom._meta.verbose_name,
                        history    =   "删除 [%s]" %(str(data_item)),
                        historyAction = data_item.status
                )  
                      
                models.Bom.objects.filter(id=record_id).delete()    
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
        elif action.lower() == "add":
            value = json.loads(req.POST.get("value"))
            if value: 
                try:
                    data_item = models.Bom.objects.create( 
                        status=models.DataStatus.objects.filter(statusName="新规")[0],
                        owner = views_auth.getCurUser(req),   
                        **value)
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']= views.ErrorInfo.exists_error
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   views_auth.getCurUser(req),
                        log_table  =   models.Bom._meta.verbose_name,
                        log_action =   "add %s" %(value)
                    )  
                      
                    # 变更为新规状态
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Bom._meta.verbose_name,
                        history    =   "新规 [%s]" %(str(data_item)),
                        historyAction = data_item.status
                    )    
            else:
                response_dict['status'] = False
                response_dict['data']   = views.ErrorInfo.data_error
                                
        elif action.lower() == "update":
            value = json.loads(req.POST.get("value"))
            record_id = req.POST.get("id")

            if not value:
                response_dict['status'] = False
                response_dict['data']   = views.ErrorInfo.data_error
            elif value[0] == value[1]:
                response_dict['status'] = False
                response_dict['data']   = views.ErrorInfo.nochange_error
            else:
                try:
                    models.Bom.objects.filter(id=record_id).update(
                        status=models.DataStatus.objects.filter(statusName="变更")[0],
                        owner = views_auth.getCurUser(req),
                        **value[1])                    
                    
                except Exception as e:
                    print(e)
                    response_dict['status'] = False
                    response_dict['data']   = views.ErrorInfo.update_error
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   views_auth.getCurUser(req),
                        log_table  =   models.Product._meta.verbose_name,
                        log_action =   "update %s->%s" %(value[0],value[1])
                    )
                    
                    # 变更为变更状态
                    data_item = models.Bom.objects.filter(id=record_id)[0]
                    modify_list = []
                    for k in value[0].keys():
                        if (value[0][k] != value[1][k]):
                            modify_list.append("%s->%s" %(value[0][k], value[1][k]))
                            
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Bom._meta.verbose_name,
                        history    =   "变更 %s" %(modify_list),
                        historyAction = data_item.status
                    )   
  
    return HttpResponse(json.dumps(response_dict))
