# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speed_read', '0005_auto_20150701_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsession',
            name='closed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
