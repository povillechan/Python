# # -*- coding:utf-8 -*-
from django.db import models
# # Create your models here.
# 
class DataStatus(models.Model):
    statusName = models.CharField(max_length=32,  verbose_name="状态", blank=False)
         
    def __str__(self):
        return self.statusName
      
    class Meta:
        verbose_name = '状态'  
         
class Product(models.Model):
    productName = models.CharField(max_length=128, verbose_name="产品名")
    bom = models.ForeignKey("Bom", on_delete=models.CASCADE, verbose_name="Bom名",default=1)
    status = models.ForeignKey("DataStatus", on_delete=models.CASCADE, verbose_name="状态",default=1)
    owner = models.CharField(max_length=128, verbose_name="所有者") 
 
    def __str__(self):
        return self.productName
    class Meta:  
        unique_together = ('productName', 'bom',)
        verbose_name = '产品BOM单'  
         
class Bom(models.Model):
    bomName = models.CharField(max_length=128,  verbose_name="Bom名")
    bomVersion = models.CharField(max_length=20,  verbose_name="Bom版本") 
    bomDiscrib = models.CharField(max_length=128,  verbose_name="Bom描述", default="")
    bomContext = models.TextField(verbose_name="Bom内容")
    status = models.ForeignKey("DataStatus", on_delete=models.CASCADE, verbose_name="状态",default=1)
    owner = models.CharField(max_length=128, verbose_name="所有者") 
    
    def __str__(self):
        return self.bomName+"-"+self.bomVersion
     
    class Meta:
        unique_together = ('bomName', 'bomVersion',)
        verbose_name = 'BOM单'  
 
     
class Paper(models.Model):
    paperName = models.CharField(max_length=128,  verbose_name="图纸名", blank=False)
    paperVersion = models.CharField(max_length=20,  verbose_name="图纸版本", blank=False)
    paperDiscrib = models.CharField(max_length=128,  verbose_name="图纸描述", default="")
    paperAddr = models.TextField(max_length=256,  verbose_name="图纸地址", blank=False)
    status = models.ForeignKey("DataStatus", on_delete=models.CASCADE, verbose_name="状态",default=1)      
    owner = models.CharField(max_length=128, verbose_name="所有者")     
    
    def __str__(self):
        return self.paperName+"-"+self.paperVersion
     
    class Meta:
        unique_together = ('paperName', 'paperVersion',)
        verbose_name = '图纸'  
     
class DataHistory(models.Model):
    historyTime = models.DateTimeField(auto_now_add=True, verbose_name="时间")
    historyAction = models.ForeignKey("DataStatus", on_delete=models.CASCADE, verbose_name="操作",default=1)  
    history = models.TextField(max_length=256,   verbose_name="操作内容", blank=False)
    tableName = models.CharField(max_length=32,  verbose_name="表名", blank=False)
    recordId  = models.IntegerField(verbose_name="记录ID")
    user = models.CharField(max_length=128, verbose_name="状态", blank=False)  
  
    def __str__(self):
        return self.historyName
      
    class Meta:
        verbose_name = '履历'  
         
class DataBaseLog(models.Model):
    log_user   = models.CharField(max_length=128,  verbose_name="用户名", blank=False)
    log_time   = models.DateTimeField(auto_now=True, verbose_name="访问时间", blank=False)
    log_table  = models.CharField(max_length=128,  verbose_name="访问表名", default="")
    log_action = models.TextField(max_length=256,  verbose_name="操作", blank=False)
             
    def __str__(self):
        return self.log_user+"-"+self.log_time
     
    class Meta:
        verbose_name = '访问日志'  