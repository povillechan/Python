# Generated by Django 2.0.5 on 2018-06-04 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('View', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bom',
            name='bomContext',
            field=models.TextField(max_length=128, verbose_name='Bom内容'),
        ),
        migrations.AlterField(
            model_name='bom',
            name='bomName',
            field=models.CharField(max_length=128, verbose_name='Bom名'),
        ),
        migrations.AlterField(
            model_name='bom',
            name='bomVersion',
            field=models.CharField(max_length=20, verbose_name='Bom版本'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paperAddr',
            field=models.TextField(max_length=256, verbose_name='图纸地址'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paperDiscrib',
            field=models.CharField(default='', max_length=128, verbose_name='图纸描述'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paperName',
            field=models.CharField(max_length=128, verbose_name='图纸名'),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paperVersion',
            field=models.CharField(max_length=20, verbose_name='图纸版本'),
        ),
        migrations.AlterField(
            model_name='product2bom',
            name='productName',
            field=models.CharField(max_length=128, verbose_name='产品名'),
        ),
    ]
