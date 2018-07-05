# -*-: coding:utf-8 -*-
from django.shortcuts import render
from View import models,views_auth,views
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
import json

# Create your views here.
def product(req):
    product_table = models.Product.objects.all().order_by("productName")
    return render(req,"product/product_list.html", {"product_list":product_table, "table":models.Product._meta.verbose_name,"cur_user": views_auth.getCurUser(req)})

@views_auth.auth
def product_update(req):    
    bom_item = []
    item = None
    if req.method == "GET":
        record_id=req.GET.get('id', None)
        item = models.Product.objects.filter(id=record_id)

        if item.exists():
            item=item[0]
            boms =  models.Bom.objects.all()
            for i in boms:
                bom_item.append(str(i))            

    return render(req,"product/product_update.html", {"product":item, "bom_item":bom_item ,"cur_user": views_auth.getCurUser(req)})

def product_edit(req):
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
                data_item = models.Product.objects.filter(id=record_id)[0]

                models.DataBaseLog.objects.create(
                    log_user   =   views_auth.getCurUser(req),
                    log_table  =   models.Product._meta.verbose_name,
                    log_action =   "delete %s" %(str(data_item))
                )
          
                # 变更为删除状态
                models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Product._meta.verbose_name,
                        history    =   "删除 [%s]" %(str(data_item)),
                        historyAction = data_item.status
                )  
                      
                models.Product.objects.filter(id=record_id).delete()    
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
                response_dict['data']   = views.ErrorInfo.data_error
                
        elif action.lower() == "add":
            value = json.loads(req.POST.get("value"))
            if value:     
                try:
                    data_item = models.Product.objects.create(
                        productName=value["productName"], 
                        bom = list(filter(lambda x: str(x) == value["bomName"], models.Bom.objects.all()))[0], 
                        status=models.DataStatus.objects.filter(statusName="新规")[0],
                        owner = views_auth.getCurUser(req))                    
                except Exception as e:
                    response_dict['status'] = False
                    response_dict['data']   = views.ErrorInfo.exists_error
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   views_auth.getCurUser(req),
                        log_table  =   models.Product._meta.verbose_name,
                        log_action =   "add %s" %(value["productName"])
                    )    
                    # 变更为新规状态
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Product._meta.verbose_name,
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
                    models.Product.objects.filter(id=record_id).update(
                        productName=value[1]["productName"], 
                        bom = list(filter(lambda x: str(x) == value[1]["bomName"], models.Bom.objects.all()))[0],
                        status=models.DataStatus.objects.filter(statusName="变更")[0],
                        owner = views_auth.getCurUser(req))                    
                    
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
                    data_item = models.Product.objects.filter(id=record_id)[0]
                    modify_list = []
                    for k in value[0].keys():
                        if (value[0][k] != value[1][k]):
                            modify_list.append("%s->%s" %(value[0][k], value[1][k]))
                            
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Product._meta.verbose_name,
                        history    =   "变更 %s" %(modify_list),
                        historyAction = data_item.status
                    )   
  
    return HttpResponse(json.dumps(response_dict))

@views_auth.auth
def product_add(req):
    bom_item = []
    if req.method == "GET":
        boms =  models.Bom.objects.all()
        for i in boms:
            bom_item.append(str(i))            

    return render(req,"product/product_add.html", {"bom_item":bom_item ,"cur_user": views_auth.getCurUser(req)}) 
    