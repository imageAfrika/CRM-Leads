# Generated by Django 5.1.5 on 2025-02-07 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_alter_document_document_type_alter_quote_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='receipt_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
