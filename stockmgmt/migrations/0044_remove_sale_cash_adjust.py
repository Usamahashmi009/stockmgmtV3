# Generated by Django 4.2.6 on 2023-11-27 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0043_sale_cash_adjust'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='cash_adjust',
        ),
    ]