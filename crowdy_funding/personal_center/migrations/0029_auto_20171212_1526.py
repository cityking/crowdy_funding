# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-12 07:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0028_auto_20171212_1524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='create_time',
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 12, 15, 26, 12, 343157), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 12, 15, 26, 12, 343425), verbose_name='上次登录'),
        ),
    ]