# Generated by Django 4.2.6 on 2023-11-29 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0045_profitinformation'),
    ]

    operations = [
        migrations.CreateModel(
            name='COGSModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cogs_sum', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.DeleteModel(
            name='ProfitInformation',
        ),
    ]