from django.db import models

# Create your models here.
class Product(models.Model):
    name= models.CharField(max_length=100)
    brand = models.CharField(max_length=100,blank=True)
    stock= models.PositiveBigIntegerField(default=0)
    buying_price = models.DecimalField(max_digits=10,decimal_places=2)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2)
    def __str(self):
        return self.name
    