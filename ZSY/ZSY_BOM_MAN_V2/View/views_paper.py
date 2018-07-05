# -*-: coding:utf-8 -*-
from django.shortcuts import render
from View import models,views_auth,syndata,views
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
import json

# Create your views here.
def paper(req):
    paper_list = []
    if req.method == "GET":
        paperName = req.GET.get("paperName","")
        paperVersion = req.GET.get("paperVersion", "")
        if paperName == "" or paperVersion == "":
            paper_table = models.Paper.objects.all().order_by("paperName")
            for item in paper_table:
                paper_list.append({'paperName':item.paperName, "paperVersion":item.paperVersion, "paperDiscrib":item.paperDiscrib, "paperAddr":item.paperAddr, "id":item.id})
        else:
            item = models.Paper.objects.filter(paperName=paperName, paperVersion=paperVersion)
            if item.exists():
                paper_list.append({'paperName':item[0].paperName, "paperVersion":item[0].paperVersion, "paperDiscrib":item[0].paperDiscrib, "paperAddr":item[0].paperAddr, "id":item[0].id})
    
    return render(req,"paper/paper_list.html", {"paper_list":paper_list, "table":models.Paper._meta.verbose_name,"cur_user": views_auth.getCurUser(req)})

def paper_search(req):
    if req.method == "GET":
        record_id = req.GET.get("id",None)
        if not record_id:
            return HttpResponse("图纸输入有误")
    else:
        HttpResponse("图纸输入有误")
    
    bom_table = models.Bom.objects.all()
    if not bom_table.exists():
        HttpResponse("无法查到BOM信息")
    
    bom_name=[]
    for item in bom_table:
        bom_name.append((item.bomName,item.bomVersion))
    
    paper_s = models.Paper.objects.filter(id=record_id)[0]
    bomTable = getBomInBom(bom_name)
    bom_dict = paperSearchBom(bomTable, paper_s.paperName, paper_s.paperVersion)
    
    paper_item = []
    papers =  models.Paper.objects.all()
    for i in papers:
        paper_item.append(str(i))      
            
    return  render(req,"paper/paper_search.html", {"bom_dict":bom_dict,"paper_item":paper_item,"paperName":paper_s.paperName, "paperVersion":paper_s.paperVersion, "cur_user": views_auth.getCurUser(req)})

def paperSearchBom(bomTable, paperName, paperVersion):
    result=[]
    for bomItem in bomTable:
        item = models.Bom.objects.filter(bomName=bomItem[0],bomVersion=bomItem[1])
        if not item.exists():
            continue
        
        item = item[0]
        content = json.loads(item.bomContext)
        for key in content:
            if "图纸" in key:
                paper_key = key["图纸"]
                if paper_key:
                    for papers in paper_key:
                        if  papers["图纸名"] == paperName and  papers["版本"] == paperVersion:
                            for productItem in item.product_set.all():  
                                subItem={"bomName":item.bomName, "bomVersion":item.bomVersion, "productName":productItem.productName}  
                                if subItem not in result:
                                    result.append(subItem)                  
            else:
                pass

    return result


def getBomInBom(bomTable):
    for bomItem in bomTable:
        item = models.Bom.objects.filter(bomName=bomItem[0],bomVersion=bomItem[1])
        if not item.exists():
            continue
        
        item = item[0]
        content = json.loads(item.bomContext)
        for key in content:
            if "Bom" in key:
                bom_key = key["Bom"]
                if bom_key:
                    for boms in bom_key:
                        bom_info = (boms["Bom名"], boms["版本"])
                        if bom_info not in bomTable:
                            bomTable.append(bom_info)
            else:
                pass
    return bomTable

@views_auth.auth
def paper_update(req):    
    if req.method == "GET":
        record_id=req.GET.get('id', None)
        item = models.Paper.objects.filter(id=record_id)
 
        if item.exists():
            item = item[0]
    return render(req,"paper/paper_update.html", {"paper_item":item , "cur_user": views_auth.getCurUser(req)})

@views_auth.auth
def paper_add(req):
#     item_name={}
#     item_verbose_name=[]
#     message = ""
# 
#     for item in models.Paper._meta.get_fields():       
#         if not item.auto_created:
#             item_name[item.verbose_name] = item.name
#             item_verbose_name.append(item.verbose_name)
#             
#     if req.method == "GET":
#         return render(req,"paper/paper_add.html", {"item_name":item_name, "cur_user": views_auth.getCurUser(req), 'msg': message})
    
    return render(req,"paper/paper_add.html", {"cur_user": views_auth.getCurUser(req)})  

def paper_edit(req):
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
                data_item = models.Paper.objects.filter(id=record_id)[0]
                models.DataBaseLog.objects.create(
                           log_user   =   views_auth.getCurUser(req),
                           log_table  =   models.Paper._meta.verbose_name,
                           log_action =   "delete %s" %(str(data_item))
                        )    
                # 变更为删除状态
                models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Paper._meta.verbose_name,
                        history    =   "删除 [%s]" %(str(data_item)),
                        historyAction = data_item.status
                )   
                
                models.Paper.objects.filter(id=record_id).delete() 
                                        
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
                response_dict['data']   = views.ErrorInfo.data_error
                
        elif action.lower() == "add":
            value = json.loads(req.POST.get("value"))

            if value:
                try:
                    data_item = models.Paper.objects.create( 
                        status=models.DataStatus.objects.filter(statusName="新规")[0],
                        owner = views_auth.getCurUser(req),   
                        **value)
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']   = views.ErrorInfo.exists_error
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   views_auth.getCurUser(req),
                        log_table  =   models.Paper._meta.verbose_name,
                        log_action =   "add %s" %(value)
                    )      
                       
                    # 变更为新规状态
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Paper._meta.verbose_name,
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
                    models.Paper.objects.filter(id=record_id).update(                       
                        status=models.DataStatus.objects.filter(statusName="变更")[0],
                        owner = views_auth.getCurUser(req),
                        **value[1])       
                except Exception: 
                    response_dict['status'] = False
                    response_dict['data']   = views.ErrorInfo.update_error
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   views_auth.getCurUser(req),
                        log_table  =   models.Paper._meta.verbose_name,
                        log_action =   "update %s to %s" %(value[0], value[1])
                    )   
                                       
                    # 变更为变更状态
                    data_item = models.Paper.objects.filter(id=record_id)[0]
                    modify_list = []
                    for k in value[0].keys():
                        if (value[0][k] != value[1][k]):
                            modify_list.append("%s->%s" %(value[0][k], value[1][k]))
                            
                    models.DataHistory.objects.create(
                        user       =   views_auth.getCurUser(req),
                        recordId   =   data_item.id,
                        tableName  =   models.Paper._meta.verbose_name,
                        history    =   "变更 %s" %(modify_list),
                        historyAction = data_item.status
                    )                       
                    syndata.synchPaper(value[0], value[1], req)
                    
        elif action.lower() == "modify":
            item_value = json.loads(req.POST.get("data"))
 
            paperName = None
            paperVersion = None
            papers =  models.Paper.objects.all().filter()
            for item in papers:
                if str(item) == item_value[0]["paper_new"]:
                    paperName =  item.paperName
                    paperVersion = item.paperVersion
                    break
            
            syndata.synchPaperModify(paperName, paperVersion, *item_value)
            
    return HttpResponse(json.dumps(response_dict))
