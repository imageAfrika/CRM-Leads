# Generated by Django 5.1.6 on 2025-02-19 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pin',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
