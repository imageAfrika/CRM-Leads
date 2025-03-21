# Generated by Django 5.1.5 on 2025-02-07 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('documents', '0005_expenditure'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={},
        ),
        migrations.AddField(
            model_name='document',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('SENT', 'Sent'), ('PAID', 'Paid'), ('OVERDUE', 'Overdue')], default='DRAFT', max_length=10),
        ),
        migrations.AddField(
            model_name='document',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='document',
            name='tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='document',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='document',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.client'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('SENT', 'Sent'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('INVOICED', 'Invoiced')], default='DRAFT', max_length=20),
        ),
    ]
