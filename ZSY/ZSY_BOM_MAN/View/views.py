# -*-: coding:utf-8 -*-
from django.shortcuts import render
from View import models,auth,syndata
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
import json

# Create your views here.
def index(req):
    return render(req,"index.html", {"cur_user": auth.getCurUser(req)})

def product(req):
    product_table = models.Product2Bom.objects.all().order_by("productName")
    product_list = []
    for item in product_table:
        product_list.append({'productName':str(item), "bomName":item.bomName.bomName, "bomVersion":item.bomName.bomVersion})
    
 
    return render(req,"product/product_list.html", {"product_list":product_list, "cur_user": auth.getCurUser(req)})

@auth.auth
def product_update(req):    
    bom_item = []
    bom_name = None
    if req.method == "GET":
        productName=req.GET.get('productName', None)
        item = models.Product2Bom.objects.filter(productName=productName)

        if item.exists():
            item=item[0]
            bom_name = str(item.bomName)
            boms =  models.Bom.objects.all()
            for i in boms:
                bom_item.append(str(i))            

    return render(req,"product/product_update.html", {"product_name":productName ,"bom_name":bom_name, "bom_item":bom_item ,"cur_user": auth.getCurUser(req)})

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
            productName=req.POST.get('productName', None)
            if productName:
                models.Product2Bom.objects.filter(productName=productName).delete()
                models.DataBaseLog.objects.create(
                    log_user   =   auth.getCurUser(req),
                    log_table  =   models.Product2Bom._meta.verbose_name,
                    log_action =   "delete %s-%s" %(productName)
                )   
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
                
        elif action.lower() == "add":
            productName=req.POST.get("productName", None)
            bomName=req.POST.get("bomName", None)
            if productName and bomName:                           
                try:
                    a  = list(filter(lambda x: str(x) == bomName, models.Bom.objects.all()))
                    models.Product2Bom.objects.create(productName=productName, bomName = a[0])
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']="添加失败，请检查输入是否有误，或者已存在相同的记录！"
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Product2Bom._meta.verbose_name,
                        log_action =   "add %s" %(productName)
                    )    
            else:
                response_dict['status'] = False
                response_dict['data']="添加失败，请检查输入是否有误，或者已存在相同的记录！"
                         
        elif action.lower() == "update":
            value_before = {}
            value_after = {}
            for item in models.Product2Bom._meta.get_fields():   
                if not item.auto_created:
                    value_before[item.name] = req.POST.get("before[%s]" % (item.name), None)
                    value_after[item.name] = req.POST.get("after[%s]" % (item.name), None)
             
            if value_before == value_after:
                response_dict['status'] = False
                response_dict['data']="未做任何修改！"
            else:
                try:
                    a  = list(filter(lambda x: str(x) == value_after["bomName"], models.Bom.objects.all()))
                    models.Product2Bom.objects.filter(productName=value_before["productName"]).update(productName=value_after["productName"], bomName = a[0] ) 
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']="更新失败，请检查输入是否有误，或者已存在相同的记录！"   
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Product2Bom._meta.verbose_name,
                        log_action =   "update %s to %s" %(value_before, value_after)
                    )    
                
    return HttpResponse(json.dumps(response_dict))

@auth.auth
def product_add(req):
    bom_item = []
    if req.method == "GET":
        boms =  models.Bom.objects.all()
        for i in boms:
            bom_item.append(str(i))            

    return render(req,"product/product_add.html", {"bom_item":bom_item ,"cur_user": auth.getCurUser(req)}) 
        

def paper(req):
    paper_list = []
    if req.method == "GET":
        paperName = req.GET.get("paperName","")
        paperVersion = req.GET.get("paperVersion", "")
        if paperName == "" or paperVersion == "":
            paper_table = models.Paper.objects.all().order_by("paperName")
            for item in paper_table:
                paper_list.append({'paperName':item.paperName, "paperVersion":item.paperVersion, "paperDiscrib":item.paperDiscrib, "paperAddr":item.paperAddr})
        else:
            item = models.Paper.objects.filter(paperName=paperName, paperVersion=paperVersion)
            if item.exists():
                paper_list.append({'paperName':item[0].paperName, "paperVersion":item[0].paperVersion, "paperDiscrib":item[0].paperDiscrib, "paperAddr":item[0].paperAddr})
    
    return render(req,"paper/paper_list.html", {"paper_list":paper_list, "cur_user": auth.getCurUser(req)})

def paper_search(req):
    if req.method == "GET":
        paperName = req.GET.get("paperName","")
        paperVersion = req.GET.get("paperVersion", "")
        if paperName == "" or paperVersion == "":
            return HttpResponse("图纸输入有误")
    else:
        HttpResponse("图纸输入有误")
    
    bom_table = models.Bom.objects.all()
    if not bom_table.exists():
        HttpResponse("无法查到BOM信息")
    
    bom_name=[]
    for item in bom_table:
        bom_name.append((item.bomName,item.bomVersion))
    
    bomTable = getBomInBom(bom_name)
    bom_dict = paperSearchBom(bomTable, paperName, paperVersion)
    
    paper_item = []
    papers =  models.Paper.objects.all()
    for i in papers:
        paper_item.append(str(i))      
            
    return  render(req,"paper/paper_search.html", {"bom_dict":bom_dict,"paper_item":paper_item,"paperName":paperName, "paperVersion":paperVersion, "cur_user": auth.getCurUser(req)})

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
                            for productItem in item.product2bom_set.all():
  
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

@auth.auth
def paper_update(req):    
    paper_item = []
    if req.method == "GET":
        paperName=req.GET.get('paperName', None)
        paperVersion=req.GET.get('paperVersion', None)
        item = models.Paper.objects.filter(paperName=paperName, paperVersion=paperVersion)
 
        if item.exists():
            item = item[0]

            for i in item._meta.get_fields():
                if not i.auto_created:
                    p_item = []
                    p_item.append(i.verbose_name)
                    p_item.append(i.name)
                    p_item.append(getattr(item, i.name))
                    paper_item.append(p_item)
    return render(req,"paper/paper_update.html", {"paper_item":paper_item , "cur_user": auth.getCurUser(req)})

@auth.auth
def paper_add(req):
    item_name={}
    item_verbose_name=[]
    message = ""

    for item in models.Paper._meta.get_fields():       
        if not item.auto_created:
            item_name[item.verbose_name] = item.name
            item_verbose_name.append(item.verbose_name)
            
    if req.method == "GET":
        return render(req,"paper/paper_add.html", {"item_name":item_name, "cur_user": auth.getCurUser(req), 'msg': message})
    
    return render(req,"paper/paper_add.html", {"item_name":item_name, "cur_user": auth.getCurUser(req), 'msg': message})  

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
            paperName=req.POST.get('paperName', None)
            paperVersion=req.POST.get('paperVersion', None)
            if paperName and paperVersion:
                models.Paper.objects.filter(paperName=paperName,paperVersion=paperVersion).delete()
                models.DataBaseLog.objects.create(
                           log_user   =   auth.getCurUser(req),
                           log_table  =   models.Paper._meta.verbose_name,
                           log_action =   "delete %s-%s" %(paperName, paperVersion)
                        )                                            
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
                
        elif action.lower() == "add":
            item_value = {}
            for item in models.Paper._meta.get_fields():   
                if not item.auto_created:
                    item_value[item.name] = req.POST.get(item.name, None)
            try:
                models.Paper.objects.create(**item_value)
            except Exception:
                response_dict['status'] = False
                response_dict['data']="添加失败，请检查输入是否有误，或者已存在相同的记录！"
            else:
                models.DataBaseLog.objects.create(
                    log_user   =   auth.getCurUser(req),
                    log_table  =   models.Paper._meta.verbose_name,
                    log_action =   "add %s" %(item_value)
                )      
                         
        elif action.lower() == "update":
            value_before = {}
            value_after = {}
            for item in models.Paper._meta.get_fields():   
                if not item.auto_created:
                    value_before[item.name] = req.POST.get("before[%s]" % (item.name), None)
                    value_after[item.name] = req.POST.get("after[%s]" % (item.name), None)
                    
 
            
            if value_before == value_after:
                response_dict['status'] = False
                response_dict['data']="未做任何修改！"
            else:
                try:
                    models.Paper.objects.filter(**value_before).update(**value_after)
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']="更新失败，请检查输入是否有误，或者已存在相同的记录！"   
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Paper._meta.verbose_name,
                        log_action =   "update %s to %s" %(value_before, value_after)
                    )   
                    
                    syndata.synchPaper(value_before, value_after)
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
    
def bom_detail(req):
    if req.method == "GET":
        bomName = req.GET.get("bomName","")
        bomVersion = req.GET.get("bomVersion", "")
 
        if bomName == "" or bomVersion == "":
            return HttpResponse("无法找到Bom信息")
        
        bom = models.Bom.objects.filter(bomName=bomName, bomVersion=bomVersion)
        if bom.exists():
            return render(req,"bom/bom_detail.html", {"bomName":bomName, "bomVersion":bomVersion, "bom_list":json.dumps(bom[0].bomContext), "cur_user": auth.getCurUser(req)})
            
        return HttpResponse("无法找到Bom信息")
    
       
def bom(req):
    bom_table = models.Bom.objects.all().order_by("bomName")
    bom_list = []
    for item in bom_table:
        bom_list.append({"bomName":item.bomName, "bomVersion":item.bomVersion})
    
    return render(req,"bom/bom_list.html", {"bom_list":bom_list, "cur_user": auth.getCurUser(req)})

@auth.auth
def bom_update(req):
    if req.method == "GET":
        bomName = req.GET.get("bomName",None)
        bomVersion = req.GET.get("bomVersion", None)
 
        if not bomName or not bomVersion:
            return HttpResponse("无法找到Bom信息")
        
        bom = models.Bom.objects.filter(bomName=bomName, bomVersion=bomVersion)
        if bom.exists():
            return render(req,"bom/bom_update.html", {"bomName":bomName, "bomVersion":bomVersion, "bom_list":json.dumps(bom[0].bomContext), "cur_user": auth.getCurUser(req)})
            
    return HttpResponse("无法找到Bom信息")

@auth.auth
def bom_add(req):
    item_name={}
    item_verbose_name=[]
    message = ""

    for item in models.Bom._meta.get_fields():       
        if not item.auto_created:
            item_name[item.verbose_name] = item.name
            item_verbose_name.append(item.verbose_name)
            
    if req.method == "GET":
        return render(req,"bom/bom_add.html", {"item_name":item_name, "cur_user": auth.getCurUser(req), 'msg': message})
    
    return render(req,"bom/bom_add.html", {"item_name":item_name, "cur_user": auth.getCurUser(req), 'msg': message})  

@auth.auth
def bom_clone(req):
    if req.method == "GET":
        bomName = req.GET.get("bomName",None)
        bomVersion = req.GET.get("bomVersion", None)
 
        if not bomName or not bomVersion:
            return HttpResponse("无法找到Bom信息")
        
        bom = models.Bom.objects.filter(bomName=bomName, bomVersion=bomVersion)
        if bom.exists():
            return render(req,"bom/bom_add.html", {"bomName":bomName, "bomVersion":bomVersion, "bom_list":json.dumps(bom[0].bomContext), "bom_action":"clone","cur_user": auth.getCurUser(req)})
            
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
            bomName=req.POST.get('bomName', None)
            bomVersion=req.POST.get('bomVersion', None)
 
            if bomName and bomVersion:
                models.Bom.objects.filter(bomName=bomName,bomVersion=bomVersion).delete()
                models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Bom._meta.verbose_name,
                        log_action =   "delete %s-%s" %(bomName, bomVersion)
                    ) 
            else:
                response_dict['status'] = False
                response_dict['error'] = "errData"
        elif action.lower() == "add":
            bomName =req.POST.get('bomName', None)
            bomVersion = req.POST.get('bomVersion', None)
            bom = req.POST.get('bom', None)

            if bomName and bomVersion and bom:
                try:
                    models.Bom.objects.create(bomName=bomName,bomVersion=bomVersion,bomContext=bom)
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']="添加失败，请检查输入是否有误，或者已存在相同的记录！" 
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Bom._meta.verbose_name,
                        log_action =   "add %s %s" %(bomName, bomVersion)
                    )   
            else:
                response_dict['status'] = False
                response_dict['data']="添加失败，请检查输入是否有误，或者已存在相同的记录！"   
                                
        elif action.lower() == "update":
            bomName =req.POST.get('bomName', None)
            bomVersion = req.POST.get('bomVersion', None)
            bomOldName =req.POST.get('bomOldName', None)
            bomOldVersion =req.POST.get('bomOldVersion', None)
            bom = req.POST.get('bom', None)
            if bomName and bomVersion and bomOldName and bomOldVersion and bom:
                try:
                    models.Bom.objects.filter(bomName=bomOldName,bomVersion=bomOldVersion).update(bomName=bomName,bomVersion=bomVersion,bomContext=bom)
                except Exception:
                    response_dict['status'] = False
                    response_dict['data']="更新失败，请检查输入是否有误，或者已存在相同的记录！"   
                else:
                    models.DataBaseLog.objects.create(
                        log_user   =   auth.getCurUser(req),
                        log_table  =   models.Bom._meta.verbose_name,
                        log_action =   "update %s-%s to %s-%s" %(bomOldName, bomOldVersion, bomName, bomVersion)
                    )   
            else:
                response_dict['status'] = False
                response_dict['data']="更新失败，请检查输入是否有误，或者已存在相同的记录！"   
            

    return HttpResponse(json.dumps(response_dict))
