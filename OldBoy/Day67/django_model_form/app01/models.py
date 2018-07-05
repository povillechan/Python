from django.db import models
from django.core.validators import RegexValidator


# Create your models here.
class News(models.Model):
    title = models.CharField(max_length=10,
                             error_messages={'c1': '.....'},
                             validators=[
                                 RegexValidator(regex='root_\d+', message='错误了', code='c1'),]
                             )
    favor = models.ManyToManyField('User', through="Favor", through_fields=("new_obj", 'user_obj'))


class User(models.Model):
    name = models.CharField(max_length=10)
    email = models.EmailField(max_length=10)
    user_type = models.ForeignKey('UserType')  # 一对多


# file = models.FileField(upload_to='upload')
#     w=models.IntegerField()
#     h=models.IntegerField()
#     file = models.ImageField(upload_to='upload',width_field='w',height_field='h')
#     # user_profile = models.ForeignKey('UserDetail',unique=True)
#     user_profile = models.OneToOneField('UserDetail')
#
# class UserDetail(models.Model):
#     pwd = models.CharField(max_length=32)


class Favor(models.Model):
    new_obj = models.ForeignKey('News', related_name="n")
    user_obj = models.ForeignKey('User', related_name='u')
    name = models.CharField(max_length=64, null=True, blank=True)


class UserType(models.Model):
    name = models.CharField(max_length=10)
