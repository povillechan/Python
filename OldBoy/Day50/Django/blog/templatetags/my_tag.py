# -*- coding:utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# 最多两个参数
@register.filter
def my_add100(v1):
    return v1 + 100

@register.filter
def my_add101(v1,v2):
    return v1 + 101 + v2

#不能用if
@register.simple_tag
def my_add(v1, v2, v3):
    return v1 + v2 + v3
