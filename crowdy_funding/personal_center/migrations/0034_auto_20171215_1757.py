# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-15 09:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0033_auto_20171215_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='balance',
            field=models.FloatField(default=0, verbose_name='钱包余额'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 15, 17, 57, 24, 248761), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 15, 17, 57, 24, 249012), verbose_name='上次登录'),
        ),
    ]