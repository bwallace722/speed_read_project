# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprehensionQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('stop_time', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Passage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('passage_title', models.CharField(default=b'', max_length=200)),
                ('passage_text', models.TextField()),
                ('words_in_passage', models.IntegerField(default=0, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionExercise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(choices=[(2, 'unattempted'), (0, 'incorrect'), (1, 'correct')])),
                ('exercise', models.ForeignKey(to='speed_read.Exercise')),
                ('question', models.ForeignKey(to='speed_read.ComprehensionQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('completion_time', models.DateTimeField(null=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('current_exercise', models.ForeignKey(default=None, to='speed_read.Exercise', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='exercise',
            name='passage',
            field=models.ForeignKey(to='speed_read.Passage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='training_session',
            field=models.ForeignKey(to='speed_read.TrainingSession'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comprehensionquestion',
            name='exercises',
            field=models.ManyToManyField(to='speed_read.Exercise', through='speed_read.QuestionExercise'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comprehensionquestion',
            name='passage',
            field=models.ForeignKey(to='speed_read.Passage'),
            preserve_default=True,
        ),
    ]
