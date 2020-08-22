# Generated by Django 3.0.5 on 2020-08-10 09:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0008_auto_20200810_0539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chore',
            name='last_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recently_completed_chores', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chore',
            name='next_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='upcoming_chores', to=settings.AUTH_USER_MODEL),
        ),
    ]
