from django.db import models

# Create your models here.

class SalesRecord(models.Model):
    date = models.DateField()
    region = models.CharField(max_length=100)
    product = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    revenue = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.date} | {self.region} | {self.product}"
