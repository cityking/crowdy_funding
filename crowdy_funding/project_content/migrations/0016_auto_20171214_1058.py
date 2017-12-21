# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-14 02:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0015_auto_20171214_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminfo',
            name='item_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_content.ItemType', verbose_name='项目类型'),
        ),
    ]
