# Generated by Django 4.2.6 on 2023-12-05 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0059_alter_cogsmodel_cogs_sum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemsmodel',
            name='category',
        ),
    ]
