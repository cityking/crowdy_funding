# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-01 03:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0011_userpayback_delete_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='银行名称')),
            ],
        ),
        migrations.AlterModelOptions(
            name='report',
            options={},
        ),
        migrations.AddField(
            model_name='payback',
            name='is_delivery',
            field=models.CharField(default='0', max_length=2, verbose_name='是否要快递'),
        ),
        migrations.AddField(
            model_name='userpayback',
            name='content',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='回报内容'),
        ),
        migrations.AlterField(
            model_name='userpayback',
            name='delete_status',
            field=models.CharField(default='0', max_length=2, verbose_name='删除状态'),
        ),
        migrations.AlterField(
            model_name='userpayback',
            name='status',
            field=models.CharField(choices=[('0', '待回报'), ('1', '已回报')], max_length=2, verbose_name='回报状态'),
        ),
    ]