'''
Created on 2018年6月25日

@author: chenzf
'''
from django.dispatch import dispatcher
from django.db.models.signals import post_migrate
from View import models
 
#定义receiver函数
def init_db(sender, **kwargs):
#     print(sender.__dict__)
    if sender.name == "View":
        if not models.DataStatus.objects.exists():
            models.DataStatus.objects.create(statusName="不明")
            models.DataStatus.objects.create(statusName="发布")  
            models.DataStatus.objects.create(statusName="删除")
            models.DataStatus.objects.create(statusName="评审")
            models.DataStatus.objects.create(statusName="草稿")
            models.DataStatus.objects.create(statusName="变更")
            models.DataStatus.objects.create(statusName="新规")
  
post_migrate.connect(init_db)