from django.db import models

class Price(models.Model):

    class Meta:
        unique_together = (("item_id", "date"))

    item_id = models.CharField(max_length=12, primary_key=True)
    date = models.DateField()
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()