# Generated by Django 4.1.3 on 2023-01-22 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_alter_watchlist_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='date_added',
            field=models.DateField(verbose_name='YYYY-MM-DD'),
        ),
    ]