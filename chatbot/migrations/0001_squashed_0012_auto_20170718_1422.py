# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import chatbot.script.file_storage


class Migration(migrations.Migration):

    replaces = [(b'chatbot', '0001_initial'), (b'chatbot', '0002_auto_20161021_0938'), (b'chatbot', '0003_auto_20161021_1046'), (b'chatbot', '0004_auto_20161024_1357'), (b'chatbot', '0005_auto_20161024_1549'), (b'chatbot', '0006_auto_20161026_0951'), (b'chatbot', '0007_auto_20161101_1210'), (b'chatbot', '0008_remove_aiml_file_content'), (b'chatbot', '0009_auto_20161104_1623'), (b'chatbot', '0010_cbot_twit_capable'), (b'chatbot', '0011_auto_20170718_1404'), (b'chatbot', '0012_auto_20170718_1422')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='aiml_config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=100, blank=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False, verbose_name=b'Should be public?')),
            ],
            options={
                'verbose_name': 'Personality',
                'verbose_name_plural': 'Personalities',
            },
        ),
        migrations.CreateModel(
            name='aiml_file',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('docfile', models.FileField(storage=chatbot.script.file_storage.MyFileStorage(), max_length=500, upload_to=b'')),
                ('text_file', models.TextField(default=b'', verbose_name=b'File Contents', blank=True)),
                ('author', models.ForeignKey(related_name='aiml', default=1, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'File',
            },
        ),
        migrations.CreateModel(
            name='cbot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Date created')),
                ('title', models.CharField(default=b'', max_length=100)),
                ('pandora_name', models.CharField(default=b'', unique=True, max_length=70)),
                ('enabled', models.BooleanField(default=False, verbose_name=b'Is enabled?')),
                ('twit_hashtags', models.CharField(default=b'', max_length=200, verbose_name=b'Hashtags and Keywords', blank=True)),
                ('twit_token', models.CharField(default=b'', help_text=b'Stuff', max_length=200, verbose_name=b'Twitter Access Token')),
                ('twit_token_secret', models.CharField(default=b'', max_length=200, verbose_name=b'Twitter Access Token Secret')),
                ('twit_c_key', models.CharField(default=b'', max_length=200, verbose_name=b'Twitter Consumer Key')),
                ('twit_c_secret', models.CharField(default=b'', max_length=200, verbose_name=b'Twitter Consumer Secret')),
                ('aiml_config', models.ManyToManyField(related_name='mlconfig', verbose_name=b'Active Chatbot Setups', to=b'chatbot.aiml_config', blank=True)),
                ('author', models.ForeignKey(related_name='chatbots', default=1, blank=True, to=settings.AUTH_USER_MODEL)),
                ('twit_capable', models.BooleanField(default=False, verbose_name=b'Is twitter capable?')),
            ],
            options={
                'verbose_name': 'Chatbot Instance',
                'verbose_name_plural': 'Chatbots',
            },
        ),
        migrations.CreateModel(
            name='pandora_settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_id', models.CharField(max_length=1000)),
                ('user_key', models.CharField(max_length=1000)),
                ('host', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'Pandora Settings',
                'verbose_name_plural': 'Pandora Settings',
            },
        ),
        migrations.AddField(
            model_name='aiml_config',
            name='aiml_files',
            field=models.ManyToManyField(related_name='AIML_File', verbose_name=b'Personality Files', to=b'chatbot.aiml_file', blank=True),
        ),
        migrations.AddField(
            model_name='aiml_config',
            name='author',
            field=models.ForeignKey(related_name='configs', default=1, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='aiml_config',
            name='public',
        ),
        migrations.AddField(
            model_name='aiml_config',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name=b'Should be public?'),
        ),
        migrations.AlterModelOptions(
            name='aiml_config',
            options={'verbose_name': 'Setup', 'verbose_name_plural': 'Setups'},
        ),
        migrations.AlterField(
            model_name='aiml_config',
            name='aiml_files',
            field=models.ManyToManyField(related_name='AIML_File', verbose_name=b'Chatbot Setups', to=b'chatbot.aiml_file', blank=True),
        ),
        migrations.AlterField(
            model_name='aiml_config',
            name='title',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AlterField(
            model_name='aiml_config',
            name='aiml_files',
            field=models.ManyToManyField(related_name='AIML_File', verbose_name=b'Current Setup Files', to=b'chatbot.aiml_file', blank=True),
        ),
    ]
