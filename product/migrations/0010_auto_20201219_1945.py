# Generated by Django 3.1.4 on 2020-12-19 14:15

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_remove_bookpage_related_titles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpage',
            name='linked_products',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, null=True, to='product.ProductPage'),
        ),
    ]