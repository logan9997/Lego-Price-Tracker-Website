from django.db import models

class Item(models.Model):
    item_id = models.CharField(max_length=20, primary_key=True)
    item_name = models.CharField(max_length=100)
    year_released = models.IntegerField()
    item_type = models.CharField(max_length=1, choices=(
        ("M","minifig"), ("S", "set")
    ))


class Price(models.Model):
    price_record = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField('%d-%m-%Y')
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    total_quantity = models.IntegerField()


class Theme(models.Model):
    theme_id = models.AutoField(primary_key=True)
    theme_path = models.CharField(max_length=140)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16)
    email = models.EmailField()
    password = models.CharField(max_length=22)


class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    condition = models.CharField(max_length=1, choices=(
        ("U", "used"), ("N", "new")
    ))
    quantity = models.IntegerField()