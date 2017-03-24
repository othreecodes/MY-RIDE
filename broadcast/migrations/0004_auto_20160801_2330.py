# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-01 22:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('broadcast', '0003_comment_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcast',
            name='bc_from',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bcfrom', to=settings.AUTH_USER_MODEL),
        ),
    ]