# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speed_read', '0003_auto_20150629_0151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainingsession',
            name='is_complete',
        ),
    ]
