from django.db import models

class Price(models.Model):
    item_id = models.CharField(max_length=12)
    date = models.DateField()
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    total_quantity = models.IntegerField()
    models.UniqueConstraint(fields=["item_id", "date"], name="itemID_date")
