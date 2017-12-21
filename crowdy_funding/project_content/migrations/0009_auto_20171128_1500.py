# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-28 07:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0008_auto_20171127_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpayback',
            name='delivery_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project_content.DeliveryCompany', verbose_name='快递公司'),
        ),
    ]