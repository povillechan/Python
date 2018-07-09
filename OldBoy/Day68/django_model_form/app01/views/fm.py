#__author:  Administrator
#date:  2016/12/29
from django.shortcuts import render
from django import forms
from django.forms import fields
from django.forms import models as models_fields
from django.core.exceptions import ValidationError
from app01 import models
class UserForm(forms.Form):
    username = fields.CharField(label='用户名')
    email = fields.EmailField(label='邮箱')

    user_type1 = fields.ChoiceField(choices=models.UserType.objects.values_list('id','name'))

    user_type2 = models_fields.ModelChoiceField(queryset=models.UserType.objects.all(),
                                                empty_label='请选择用户类型',
                                                to_field_name="id",
                                                limit_choices_to={'id':1})

    user_type3 = models_fields.ModelMultipleChoiceField(queryset=models.UserType.objects.all(),
                                                to_field_name="id",
                                                limit_choices_to={'id': 1})

    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        self.fields['user_type1'].widget.choices = models.UserType.objects.all().values_list('id', 'name')

    def clean_username(self):
        #
        value = self.cleaned_data['username']
        if value == 'root':
            return value
        else:
            raise ValidationError('你不是我的...')

    def clean(self):
        v1 = self.cleaned_data['username']
        v2 = self.cleaned_data['email']
        if v1 == "root" and v2 == "root@live.com":
            pass
        else:
            raise ValidationError('用户名或邮箱错误!!!')

        return self.cleaned_data
    # def _post_clean(self):
    #     v1 = self.cleaned_data['username']
    #     v2 = self.cleaned_data['email']
    #     if v1 == "root" and v2 == "root@live.com":
    #         pass
    #     else:
    #         self.add_error("__all__", ValidationError('用户名或邮箱错误...'))


def index(request):
    if request.method == "GET":
        obj = UserForm()
        return render(request,'fm.html',{'obj': obj})
    elif request.method == "POST":
        obj = UserForm(request.POST)
        obj.is_valid()
        # data = obj.clean()
        # obj.cleaned_data
        # print(obj.errors)
        return render(request, 'fm.html', {'obj': obj})

def test(request):

    # obj = models.News.objects.create()
    obj = models.News(title='root_12')
    obj.full_clean()

    obj.save()