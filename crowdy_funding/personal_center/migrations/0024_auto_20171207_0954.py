# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-07 01:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0023_auto_20171207_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 7, 9, 54, 31, 886018), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 7, 9, 54, 31, 886078), verbose_name='上次登录'),
        ),
    ]
