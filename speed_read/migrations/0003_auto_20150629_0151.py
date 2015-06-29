# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speed_read', '0002_auto_20150626_1334'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprehensionChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('correct', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('question', models.ForeignKey(to='speed_read.ComprehensionQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comprehensionquestion',
            name='text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questionexercise',
            name='status',
            field=models.SmallIntegerField(default=2, choices=[(2, 'unattempted'), (0, 'incorrect'), (1, 'correct')]),
            preserve_default=True,
        ),
    ]
