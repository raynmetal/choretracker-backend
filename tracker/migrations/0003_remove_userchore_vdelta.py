# Generated by Django 3.0.5 on 2020-07-29 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_auto_20200729_0527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userchore',
            name='vdelta',
        ),
    ]
