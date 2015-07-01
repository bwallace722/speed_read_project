# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speed_read', '0004_remove_trainingsession_is_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsession',
            name='accuracy_threshold',
            field=models.FloatField(default=0.5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='exercises_to_complete',
            field=models.SmallIntegerField(default=5),
            preserve_default=True,
        ),
    ]
