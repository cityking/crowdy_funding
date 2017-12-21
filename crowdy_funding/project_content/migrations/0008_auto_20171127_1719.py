# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-27 09:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0007_deliverycompany_userpayback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpayback',
            name='delivery_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_content.DeliveryCompany', verbose_name='快递公司'),
        ),
        migrations.AlterField(
            model_name='userpayback',
            name='delivery_id',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='快递单号'),
        ),
    ]