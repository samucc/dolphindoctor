# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-26 01:57
from __future__ import unicode_literals

import assets.models.utils
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0010_auto_20180307_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
            ],
        ),
        migrations.CreateModel(
            name='Gateway',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('username', models.CharField(max_length=128, verbose_name='Username')),
                ('_password', models.CharField(blank=True, max_length=256, null=True, verbose_name='Password')),
                ('_private_key', models.TextField(blank=True, max_length=4096, null=True, validators=[assets.models.utils.private_key_validator], verbose_name='SSH private key')),
                ('_public_key', models.TextField(blank=True, max_length=4096, verbose_name='SSH public key')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(max_length=128, null=True, verbose_name='Created by')),
                ('ip', models.GenericIPAddressField(db_index=True, verbose_name='IP')),
                ('port', models.IntegerField(default=22, verbose_name='Port')),
                ('protocol', models.CharField(choices=[('ssh', 'ssh'), ('rdp', 'rdp')], default='ssh', max_length=16, verbose_name='Protocol')),
                ('comment', models.CharField(blank=True, max_length=128, null=True, verbose_name='Comment')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='assets.Domain', verbose_name='Domain'),
        ),
    ]
