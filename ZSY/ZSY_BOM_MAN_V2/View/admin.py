from django.contrib import admin

# Register your models here.
from View.models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('productName', 'bom','status')
  
  
class BomAdmin(admin.ModelAdmin):
    list_display = ('bomName','bomVersion','bomDiscrib','status')
     
  
class PaperAdmin(admin.ModelAdmin):
    list_display = ('paperName', 'paperVersion', 'paperDiscrib', 'paperAddr','status')
     
class DataBaseLogAdmin(admin.ModelAdmin):
    list_display = ('log_user', 'log_time', 'log_table','log_action')
     
admin.site.register(Product, ProductAdmin)
admin.site.register(Bom, BomAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(DataBaseLog, DataBaseLogAdmin)