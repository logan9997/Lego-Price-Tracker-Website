# Generated by Django 4.1.3 on 2023-01-09 22:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=100)),
                ('year_released', models.IntegerField()),
                ('item_type', models.CharField(choices=[('M', 'minifig'), ('S', 'set')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=16, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=22)),
            ],
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('entry', models.AutoField(primary_key=True, serialize=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.user')),
            ],
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('theme_id', models.AutoField(primary_key=True, serialize=False)),
                ('theme_path', models.CharField(max_length=140)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='App.item')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('price_record', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, default='', null=True, verbose_name='%d-%m-%Y')),
                ('avg_price', models.FloatField()),
                ('min_price', models.FloatField()),
                ('max_price', models.FloatField()),
                ('total_quantity', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.item')),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('portfolio_id', models.AutoField(primary_key=True, serialize=False)),
                ('condition', models.CharField(choices=[('U', 'used'), ('N', 'new')], max_length=1)),
                ('quantity', models.IntegerField()),
                ('date_added', models.DateField(blank=True, default='', null=True, verbose_name='%d-%m-%Y')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.user')),
            ],
        ),
    ]
