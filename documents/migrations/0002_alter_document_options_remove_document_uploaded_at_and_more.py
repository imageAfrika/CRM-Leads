# Generated by Django 5.1.5 on 2025-02-03 18:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'ordering': ['-created_at'], 'verbose_name': 'Document', 'verbose_name_plural': 'Documents'},
        ),
        migrations.RemoveField(
            model_name='document',
            name='uploaded_at',
        ),
        migrations.AlterField(
            model_name='document',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='clients.client'),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('QUOTE', 'Quote'), ('INVOICE', 'Invoice'), ('DELIVERY_NOTE', 'Delivery Note'), ('PROFORMA_INVOICE', 'Proforma Invoice'), ('PAYMENT_RECEIPT', 'Payment Receipt')], max_length=20),
        ),
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(blank=True, help_text='Upload document file', null=True, upload_to='documents/'),
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_number', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SENT', 'Sent'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('EXPIRED', 'Expired')], default='DRAFT', max_length=20)),
                ('valid_until', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='clients.client')),
            ],
            options={
                'verbose_name': 'Quote',
                'verbose_name_plural': 'Quotes',
                'ordering': ['-created_at'],
            },
        ),
    ]
