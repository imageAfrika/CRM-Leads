# Generated by Django 5.1.7 on 2025-03-23 17:31

import django.db.models.deletion
import django.utils.timezone
import registration.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('card', 'Debit/Credit Card'), ('mpesa', 'M-Pesa'), ('airtel', 'Airtel Money')], max_length=20)),
                ('account_number', models.CharField(max_length=100)),
                ('account_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_annually', models.DecimalField(decimal_places=2, max_digits=10)),
                ('features', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Company Name')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Phone Number')),
                ('email', models.EmailField(max_length=254, verbose_name='Email Address')),
                ('logo', models.ImageField(blank=True, null=True, upload_to=registration.models.company_logo_path, verbose_name='Company Logo')),
                ('tax_pin', models.CharField(max_length=50, verbose_name='Tax PIN')),
                ('physical_address', models.TextField(verbose_name='Physical Address')),
                ('postal_address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Postal Address')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('database_name', models.CharField(max_length=100, unique=True)),
                ('currency', models.CharField(default='KES', max_length=3)),
                ('timezone', models.CharField(default='Africa/Nairobi', max_length=50)),
                ('admin_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_companies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('payment_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='registration.company')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registration.paymentmethod')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registration.subscriptionplan')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_reference', models.CharField(max_length=100, unique=True)),
                ('external_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='registration.company')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registration.paymentmethod')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='registration.subscription')),
            ],
        ),
    ]
