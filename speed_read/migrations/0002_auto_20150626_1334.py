# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('speed_read', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trainingsession',
            old_name='current_exercise',
            new_name='active_exercise',
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='start_time',
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='stop_time',
        ),
        migrations.AddField(
            model_name='exercise',
            name='completion_time',
            field=models.DateTimeField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 26, 18, 34, 41, 963730, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exercise',
            name='passage_start_time',
            field=models.DateTimeField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='passage_stop_time',
            field=models.DateTimeField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='questions',
            field=models.ManyToManyField(to='speed_read.ComprehensionQuestion', through='speed_read.QuestionExercise'),
            preserve_default=True,
        ),
    ]
