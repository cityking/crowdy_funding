# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-24 06:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0005_report'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payback',
            options={'verbose_name': '回报', 'verbose_name_plural': '回报'},
        ),
    ]
