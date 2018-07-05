from django.apps import AppConfig
from View import models,auth
import json

def synchPaper(PaperDataBefore, PaperDataAfter):    
    boms = models.Bom.objects.all()

    for item in boms:
        content = json.loads(item.bomContext)
        for key in content:
            if "图纸" in key:
                paper_key = key["图纸"]
                if paper_key:
                    for papers in paper_key:
                        if  papers["图纸名"] == PaperDataBefore["paperName"] and  papers["版本"] == PaperDataBefore["paperVersion"]:
                            papers["图纸名"] = PaperDataAfter["paperName"]
                            papers["版本"] = PaperDataAfter["paperVersion"]
                            item.bomContext = json.dumps(content)
                            item.save()
                            print("modify paper")
                            models.DataBaseLog.objects.create(
                                log_user   =   "backadmin",
                                log_table  =   models.Bom._meta.verbose_name,
                                log_action =   "update paper %s to %s" %(PaperDataBefore, PaperDataAfter)
                            )     
            else: 
                pass
    return True;


def synchPaperModify(paperName, paperVersion,*PaperData):    
    for item_data in PaperData:
        boms = models.Bom.objects.filter(bomName=item_data["bomName"],bomVersion=item_data["bomVersion"])
        for item in boms:
            content = json.loads(item.bomContext)
            for key in content:
                if "图纸" in key:
                    paper_key = key["图纸"]
                    if paper_key:
                        for papers in paper_key:
                            if  papers["图纸名"] == item_data["paperName_old"] and  papers["版本"] == item_data["paperVersion_old"]:
                                papers["图纸名"] = paperName
                                papers["版本"] =  paperVersion
                                item.bomContext = json.dumps(content)
                                item.save()
                                print("modify paper")
                                models.DataBaseLog.objects.create(
                                    log_user   =   "backadmin",
                                    log_table  =   models.Bom._meta.verbose_name,
                                    log_action =   "update paper %s" %(item_data)
                                )     
                else: 
                    pass
    return True;