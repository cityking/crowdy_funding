# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-27 09:19
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0013_auto_20171127_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 27, 17, 19, 33, 523774), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 27, 17, 19, 33, 523861), verbose_name='上次登录'),
        ),
    ]