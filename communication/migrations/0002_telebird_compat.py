# Generated by Django 4.2.1 on 2025-03-28 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='email',
            name='is_draft',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='email',
            name='sender_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='email',
            name='sender_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ] 