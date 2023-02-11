from django.db import models

DATE_FORMAT = '%Y-%m-%d'
DATE_DEFAULT = '1991-01-01'

class Item(models.Model):
    item_id = models.CharField(max_length=20, primary_key=True)
    item_name = models.CharField(max_length=100)
    year_released = models.IntegerField()
    item_type = models.CharField(max_length=1, choices=(
        ("M","minifig"), ("S", "set")
    ))
    views = models.IntegerField()


class Price(models.Model):
    price_record = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField(DATE_FORMAT, blank=True, null=True, default=DATE_DEFAULT)
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    total_quantity = models.IntegerField()


class Theme(models.Model):
    theme_id = models.AutoField(primary_key=True)
    theme_path = models.CharField(max_length=140)
    item = models.ForeignKey(Item, on_delete=models.CASCADE,blank=True, null=True)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16, unique=True) #USERNAME MUST BE UNIQUE
    email = models.EmailField()
    password = models.CharField(max_length=22)
    email_preference = models.CharField(max_length=14, default="All", choices=(
        ("Never", "Never"), ("Occasional", "Occasional"),
        ("All", "All")
    ))
    date_joined = models.DateField(DATE_FORMAT)
    region = models.CharField(max_length=60, default='None')


class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    condition = models.CharField(max_length=1, choices=(
        ("U", "used"), ("N", "new")
    ))
    quantity = models.IntegerField()
    date_added = models.DateField(auto_now=True)


class Watchlist(models.Model):
    entry = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date_added = models.DateField(DATE_FORMAT)