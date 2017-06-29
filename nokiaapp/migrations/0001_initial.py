# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('measure_type', models.IntegerField(choices=[(1, b'Weight (kg)'), (4, b'Height (meter)'), (5, b'Fat Free Mass (kg)'), (6, b'Fat Ratio (%)'), (8, b'Fat Mass Weight (kg)'), (9, b'Diastolic Blood Pressure (mmHg)'), (10, b'Systolic Blood Pressure (mmHg)'), (11, b'Heart Pulse (bpm)'), (54, b'SP02(%)')])),
                ('unit', models.IntegerField()),
            ],
            options={
                'db_table': 'withingsapp_measure',
            }
        ),
        migrations.CreateModel(
            name='MeasureGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grpid', models.IntegerField()),
                ('attrib', models.IntegerField(choices=[(0, b'Captured by a device, not ambiguous'), (1, b'Captured by a device, may belong to other user'), (2, b'Manually entered by user'), (4, b'Manually entered, may not be accurate')])),
                ('date', models.DateTimeField()),
                ('updatetime', models.DateTimeField()),
                ('category', models.IntegerField(choices=[(1, b'Real measurements'), (2, b'User objectives')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'withingsapp_measuregroup',
            }
        ),
        migrations.CreateModel(
            name='WithingsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('withings_user_id', models.IntegerField()),
                ('access_token', models.TextField()),
                ('access_token_secret', models.TextField()),
                ('last_update', models.DateTimeField(null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'withingsapp_withingsuser',
            }
        ),
        migrations.AddField(
            model_name='measure',
            name='group',
            field=models.ForeignKey(to='MeasureGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='measuregroup',
            unique_together=set([('user', 'grpid')]),
        ),
    ]
