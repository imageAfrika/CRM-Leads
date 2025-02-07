# Generated by Django 5.1.5 on 2025-02-07 18:16

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='description',
        ),
        migrations.AddField(
            model_name='sale',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='payment_method',
            field=models.CharField(choices=[('CASH', 'Cash'), ('CARD', 'Card'), ('BANK_TRANSFER', 'Bank Transfer')], default='CASH', max_length=20),
        ),
        migrations.AddField(
            model_name='sale',
            name='payment_status',
            field=models.CharField(choices=[('PAID', 'Paid'), ('PENDING', 'Pending'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='sale',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='sale',
            name='tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='sale',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='sale',
            name='sale_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sales.sale')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
