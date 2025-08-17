from django.db import models, transaction
from django.db.models import Sum
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    stock = models.PositiveBigIntegerField(default=0)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    @property
    def total_sales(self):
        return Sale.objects.filter(product=self).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
        
    @property
    def total_profit(self):
        total_quantity_sold = Sale.objects.filter(product=self).aggregate(Sum('quantity'))['quantity__sum'] or 0
        return (self.selling_price - self.buying_price) * total_quantity_sold

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Validate quantity
            if self.quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Calculate total price
            self.total_price = self.product.selling_price * self.quantity

            # Handle stock updates
            if self.pk is None:
                # New sale: check stock and reduce
                if self.product.stock < self.quantity:
                    raise ValueError("Insufficient stock")
                self.product.stock -= self.product.stock >= self.quantity and self.quantity or 0
            else:
                # Existing sale: adjust stock based on quantity change
                old_sale = Sale.objects.get(pk=self.pk)
                quantity_diff = self.quantity - old_sale.quantity
                if quantity_diff > 0:
                    # Increased quantity: check if enough stock for additional units
                    if self.product.stock < quantity_diff:
                        raise ValueError("Insufficient stock for additional quantity")
                    self.product.stock -= quantity_diff
                elif quantity_diff < 0:
                    # Decreased quantity: return units to stock
                    self.product.stock -= quantity_diff  # Subtracting a negative adds to stock

            # Save the product (stock changes)
            self.product.save()
            
            # Save the sale
            super().save(*args, **kwargs)

class Purchase(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
