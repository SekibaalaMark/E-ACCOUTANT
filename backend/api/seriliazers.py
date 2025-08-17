from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'stock', 'buying_price', 'selling_price']
        read_only_fields = ['id']

    def validate(self, data):
        # Validate that buying_price and selling_price are non-negative
        if data.get('buying_price') < 0:
            raise serializers.ValidationError({"buying_price": "Buying price cannot be negative."})
        if data.get('selling_price') < 0:
            raise serializers.ValidationError({"selling_price": "Selling price cannot be negative."})
        
        # Validate that stock is non-negative (already enforced by PositiveBigIntegerField, but added for clarity)
        if data.get('stock', 0) < 0:
            raise serializers.ValidationError({"stock": "Stock cannot be negative."})
        
        # Optional: Ensure selling_price is not less than buying_price (business logic)
        if data.get('selling_price') < data.get('buying_price'):
            raise serializers.ValidationError({
                "selling_price": "Selling price should not be less than buying price."
            })
        
        # Validate that name is not empty
        if not data.get('name').strip():
            raise serializers.ValidationError({"name": "Product name cannot be empty."})
        
        return data