# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-17 03:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0006_auto_20171116_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 17, 11, 0, 22, 438942), help_text='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 17, 11, 0, 22, 439071), help_text='上次登录'),
        ),
    ]