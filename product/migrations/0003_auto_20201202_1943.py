# Generated by Django 3.1.4 on 2020-12-02 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20201129_1912'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookformat',
            options={'verbose_name': 'Book Format', 'verbose_name_plural': 'Book Formats'},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'verbose_name': 'Language', 'verbose_name_plural': 'Languages'},
        ),
    ]
