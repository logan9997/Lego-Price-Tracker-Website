# Generated by Django 4.1.3 on 2023-01-22 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='date_added',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='date_added',
            field=models.DateField(auto_now=True, default='1999-12-31'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateField(auto_now=True, default='1999-12-31'),
            preserve_default=False,
        ),
    ]