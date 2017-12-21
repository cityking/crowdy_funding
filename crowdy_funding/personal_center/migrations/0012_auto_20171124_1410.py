# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-24 06:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0011_auto_20171123_1427'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'verbose_name': '用户信息', 'verbose_name_plural': '用户信息'},
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 24, 14, 10, 29, 444320), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 24, 14, 10, 29, 444435), verbose_name='上次登录'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='password',
            field=models.CharField(max_length=32, null=True, verbose_name='密码'),
        ),
    ]