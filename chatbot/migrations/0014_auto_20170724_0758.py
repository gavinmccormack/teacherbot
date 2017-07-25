# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import chatbot.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0013_auto_20170721_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbot',
            name='pandora_name',
            field=models.CharField(default=b'', unique=True, max_length=70, validators=[chatbot.validators.validate_pandora_length, django.core.validators.RegexValidator(regex=b'^[a-z0-9]+$', message=b'Only (lowercase) characters a-z and 0-9 are allowed', code=b'Pandora name can only consist of characters a-z and 0-9.')]),
        ),
    ]
