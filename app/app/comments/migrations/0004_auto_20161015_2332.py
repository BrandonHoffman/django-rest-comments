# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-15 23:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20161015_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='url',
            field=models.CharField(max_length=256),
        ),
    ]
