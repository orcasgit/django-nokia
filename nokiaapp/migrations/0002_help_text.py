# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('nokiaapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measure',
            name='group',
            field=models.ForeignKey(help_text=b"The measurement's group", to='MeasureGroup'),
        ),
        migrations.AlterField(
            model_name='measure',
            name='measure_type',
            field=models.IntegerField(choices=[(1, b'Weight (kg)'), (4, b'Height (meter)'), (5, b'Fat Free Mass (kg)'), (6, b'Fat Ratio (%)'), (8, b'Fat Mass Weight (kg)'), (9, b'Diastolic Blood Pressure (mmHg)'), (10, b'Systolic Blood Pressure (mmHg)'), (11, b'Heart Pulse (bpm)'), (54, b'SP02(%)')], help_text=b"The measurement's type, one of: 1 (Weight (kg)), 4 (Height (meter)), 5 (Fat Free Mass (kg)), 6 (Fat Ratio (%)), 8 (Fat Mass Weight (kg)), 9 (Diastolic Blood Pressure (mmHg)), 10 (Systolic Blood Pressure (mmHg)), 11 (Heart Pulse (bpm)), 54 (SP02(%))"),
        ),
        migrations.AlterField(
            model_name='measure',
            name='unit',
            field=models.IntegerField(help_text=b'Power of ten the "value" attribute should be multiplied to to get the real value. Eg : value = 20 and unit=-1 means the value really is 2.0'),
        ),
        migrations.AlterField(
            model_name='measure',
            name='value',
            field=models.IntegerField(help_text=b'Value for the measure in S.I units (kilogram, meters, etc.). Value should be multiplied by 10 to the power of "unit" to get the real value.'),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='attrib',
            field=models.IntegerField(choices=[(0, b'Captured by a device, not ambiguous'), (1, b'Captured by a device, may belong to other user'), (2, b'Manually entered by user'), (4, b'Manually entered, may not be accurate')], help_text=b"The group's attribution, one of: 0 (Captured by a device, not ambiguous), 1 (Captured by a device, may belong to other user), 2 (Manually entered by user), 4 (Manually entered, may not be accurate)"),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='category',
            field=models.IntegerField(choices=[(1, b'Real measurements'), (2, b'User objectives')], help_text=b"The group's category, one of: 1 (Real measurements), 2 (User objectives)"),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='date',
            field=models.DateTimeField(help_text=b'The datetime of the measurement(s)'),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='grpid',
            field=models.IntegerField(help_text=b'The group ID, assigned by withings'),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='updatetime',
            field=models.DateTimeField(help_text=b'The last updated datetime of the measurement(s)'),
        ),
        migrations.AlterField(
            model_name='measuregroup',
            name='user',
            field=models.ForeignKey(help_text=b"The group's user", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='withingsuser',
            name='access_token',
            field=models.TextField(help_text=b'OAuth access token'),
        ),
        migrations.AlterField(
            model_name='withingsuser',
            name='access_token_secret',
            field=models.TextField(help_text=b'OAuth access token secret'),
        ),
        migrations.AlterField(
            model_name='withingsuser',
            name='last_update',
            field=models.DateTimeField(blank=True, null=True, help_text=b"The datetime the user's withings data was last updated"),
        ),
        migrations.AlterField(
            model_name='withingsuser',
            name='user',
            field=models.OneToOneField(help_text=b'The user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='withingsuser',
            name='withings_user_id',
            field=models.IntegerField(help_text=b'The withings user ID'),
        ),
    ]
