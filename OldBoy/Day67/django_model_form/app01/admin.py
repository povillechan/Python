from django.contrib import admin
from app01 import models
# Register your models here.

admin.site.register(models.News)
admin.site.register(models.User)
admin.site.register(models.UserType)
admin.site.register(models.Favor)