# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0014_auto_20170724_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='cbot',
            name='uploaded_files',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
