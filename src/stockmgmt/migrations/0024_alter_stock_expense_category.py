# Generated by Django 4.2.6 on 2023-11-14 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0023_expense_stock_expense_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='Expense_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.expense'),
        ),
    ]