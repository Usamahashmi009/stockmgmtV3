# Generated by Django 4.2.6 on 2023-12-04 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0056_remove_module_course_itemsmodel_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='category',
        ),
    ]
