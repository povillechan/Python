# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-07 03:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
