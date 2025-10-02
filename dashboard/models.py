from django.db import models

# Create your models here.
class Investment(models.Model):
    coin = models.CharField(max_length=64)
    quantity = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)