# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-16 09:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0005_auto_20171113_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='userconsignee',
            name='consignee_default',
            field=models.CharField(default='0', max_length=2, verbose_name='默认'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 16, 17, 40, 31, 594259), help_text='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 16, 17, 40, 31, 594305), help_text='上次登录'),
        ),
    ]
