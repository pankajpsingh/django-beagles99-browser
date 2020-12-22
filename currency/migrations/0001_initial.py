# Generated by Django 3.1.3 on 2020-11-29 13:34

import datetime
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curr_code', models.CharField(max_length=3, unique=True, verbose_name='Currency Code')),
                ('curr_name', models.CharField(blank=True, max_length=15, null=True, verbose_name='Currency Name')),
                ('curr_symbol', models.CharField(blank=True, max_length=10, null=True, verbose_name='Currency Symbol')),
                ('curr_rate', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=6, verbose_name='Exchange Rate')),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
                'get_latest_by': 'curr_code',
            },
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_rate', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=6, verbose_name='Exchange Rate')),
                ('effective_date', models.DateField(default=datetime.date.today, verbose_name='Effective Date')),
                ('applicable', models.BooleanField(default=True, verbose_name='Applicable Rate')),
                ('curr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currency.currency', verbose_name='Currency')),
            ],
            options={
                'verbose_name': 'Exchange Rate',
                'verbose_name_plural': 'Exchange Rates',
                'ordering': ['-effective_date'],
                'get_latest_by': 'effective_date',
            },
        ),
    ]