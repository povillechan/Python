from django.contrib import admin

# Register your models here.
from View.models import *

class Product2BomAdmin(admin.ModelAdmin):
    list_display = ('productName', 'bomName',)
 
 
class BomAdmin(admin.ModelAdmin):
    list_display = ('bomName','bomVersion',)
    
 
class PaperAdmin(admin.ModelAdmin):
    list_display = ('paperName', 'paperVersion', 'paperAddr',)
    
class DataBaseLogAdmin(admin.ModelAdmin):
    list_display = ('log_user', 'log_time', 'log_table','log_action')
    
admin.site.register(Product2Bom, Product2BomAdmin)
admin.site.register(Bom, BomAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(DataBaseLog, DataBaseLogAdmin)