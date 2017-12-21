# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-13 08:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_content', '0014_itemtype_type_log'),
        ('admin_project', '0003_announcement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carousel_img', models.CharField(max_length=300, unique=True, verbose_name='轮播图片地址')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_content.ItemInfo', verbose_name='轮播项目')),
            ],
            options={
                'verbose_name': '轮播',
                'verbose_name_plural': '轮播',
            },
        ),
    ]