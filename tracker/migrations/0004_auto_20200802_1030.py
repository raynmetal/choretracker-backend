# Generated by Django 3.0.5 on 2020-08-02 10:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_remove_userchore_vdelta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chore',
            name='next_date',
            field=models.DateField(default=datetime.date(2020, 8, 3)),
        ),
    ]
