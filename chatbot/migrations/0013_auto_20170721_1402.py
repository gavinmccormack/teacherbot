# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import chatbot.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0012_auto_20170718_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbot',
            name='pandora_name',
            field=models.CharField(default=b'', unique=True, max_length=70, validators=[chatbot.validators.validate_pandora_length, django.core.validators.RegexValidator(regex=b'[a-z0-9]+$')]),
        ),
    ]
