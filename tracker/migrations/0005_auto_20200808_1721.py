# Generated by Django 3.0.5 on 2020-08-08 17:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_auto_20200802_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chore',
            name='next_date',
            field=models.DateField(default=datetime.date(2020, 8, 9)),
        ),
    ]
