# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-07 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adminastrator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=32, null=True, verbose_name='密码')),
                ('nick_name', models.CharField(max_length=300, unique=True, verbose_name='用户昵称')),
            ],
            options={
                'verbose_name': '管理员',
                'verbose_name_plural': '管理员',
            },
        ),
    ]
