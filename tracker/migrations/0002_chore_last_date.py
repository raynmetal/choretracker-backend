# Generated by Django 3.0.5 on 2020-07-19 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chore',
            name='last_date',
            field=models.DateField(null=True),
        ),
    ]
