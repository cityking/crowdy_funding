# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-07 08:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, unique=True, verbose_name='角色名称')),
            ],
        ),
        migrations.AddField(
            model_name='adminastrator',
            name='authority',
            field=models.CharField(default='item', max_length=32, verbose_name='权限'),
        ),
    ]
