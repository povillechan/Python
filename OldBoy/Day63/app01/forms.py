#__author:  Administrator
#date:  2016/12/20
from django import forms as DForms
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
class DetailForm(DForms.Form):
    user1 = fields.CharField()
    user2 = fields.CharField(widget=widgets.TextInput)
    user4 = fields.IntegerField()

    # 字符串
    user3 = fields.ChoiceField(choices=[(1, 'SH'), (2, 'BJ'), ])
    user5 = fields.CharField(
        widget=widgets.Select(choices=[(1, 'SH'), (2, 'BJ'), ])
    )
    user6 = fields.IntegerField(
        widget=widgets.Select(choices=[(1, 'SH'), (2, 'BJ'), ])
    )
    user7 = fields.IntegerField(
        widget=widgets.RadioSelect(choices=[(1, 'SH'), (2, 'BJ'), ])
    )

class FieldForm(DForms.Form):
    f1 = fields.CharField(
        max_length=6,
        required=True,
        initial="小虎",
        validators=[RegexValidator(r'^[0-9]+$', '11111',code='f1'), RegexValidator(r'^159[0-9]+$', '2222',code='f2')],
        error_messages={'required': '不能为空','f1': 'geshicuowu','f2': 'kajdlfkjasldf','max_length': 'taichangla'},
        label='爱抚1',
        show_hidden_initial=True,
        disabled=False,
        label_suffix="-->"
    )
    # f2 = fields.RegexField(r'^159[0-9]+$')
    f3 = fields.FileField()

    f4 = fields.ChoiceField(
        initial=2,
        choices=[(1,'赵四',),(2,"刘能"),(3,'六大脑袋')]
    )
    f5 = fields.TypedChoiceField(
        coerce=lambda x: int(x),
        initial=2,
        choices=[(1, '赵四',), (2, "刘能"), (3, '六大脑袋')]
    )

    f6 = fields.MultipleChoiceField(
        initial=[1,2],
        choices=[(1, '赵四',), (2, "刘能"), (3, '六大脑袋')]
    )
    f7 = fields.SplitDateTimeField()
    f8 = fields.FilePathField(
        path='app01',
        allow_folders=True,
        recursive=True)

class WidghtForm(DForms.Form):
    w1 = fields.CharField(widget=widgets.ClearableFileInput)

from app01 import models
class DBForm(DForms.Form):
    host = fields.CharField()
    host_type = fields.IntegerField(
        widget=widgets.Select(choices=[])
    )

    def __init__(self,*args, **kwargs):
        # 执行父类的构造方法
        super(DBForm,self).__init__(*args, **kwargs)

        self.fields['host_type'].widget.choices = models.UserType.objects.all().values_list('id','caption')

class InitialForm(DForms.Form):
    username = fields.CharField()
    user_type = fields.IntegerField(
        widget=widgets.Select(choices=[])
    )

    def __init__(self,*args, **kwargs):
        # 执行父类的构造方法
        super(InitialForm,self).__init__(*args, **kwargs)

        self.fields['user_type'].widget.choices = models.UserType.objects.all().values_list('id','caption')
