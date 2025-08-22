from rest_framework import serializers
from .models import *

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password', 'confirm_password']

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # remove confirm field
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user




from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # authenticate() checks against Django's AUTHENTICATION_BACKENDS
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        '''
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        '''

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "username": user.username,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }




class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'stock', 'buying_price', 'selling_price']
        read_only_fields = ['id']
        extra_kwargs = {
            'brand': {'required': True},
            'stock': {'required': True}
        }

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
    




class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['id', 'product', 'quantity', 'total_price', 'date']
        read_only_fields = ['id', 'total_price', 'date']

    def validate(self, data):
        # Validate quantity is positive
        if data.get('quantity') <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be positive."})

        # Validate sufficient stock for the product
        product = data.get('product')
        quantity = data.get('quantity')
        if product.stock < quantity:
            raise serializers.ValidationError({
                "quantity": f"Insufficient stock. Available: {product.stock}, Requested: {quantity}"
            })

        return data

    def create(self, validated_data):
        # Create a new Sale instance, letting the model's save method handle total_price and stock
        return Sale.objects.create(**validated_data)

    def update(self, validated_data, instance):
        # Update quantity and product, letting the model's save method handle stock adjustments
        instance.product = validated_data.get('product', instance.product)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()  # Triggers model's save method for total_price and stock updates
        return instance
    


from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Purchase, Product


class PurchaseSerializer(serializers.ModelSerializer):
    # Read-only fields that are calculated automatically
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    date = serializers.DateTimeField(read_only=True)
    
    # Optional: Include product details in the response
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_buying_price = serializers.DecimalField(source='product.buying_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id',
            'product',
            'product_name',  # Extra field for convenience
            'product_buying_price',  # Extra field for convenience
            'quantity',
            'total_cost',
            'date'
        ]
        read_only_fields = ['total_cost', 'date']

    def validate_quantity(self, value):
        """Validate that quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value

    def validate_product(self, value):
        """Validate that the product exists and has valid buying_price"""
        try:
            if value.buying_price < 0:
                raise serializers.ValidationError("Product buying price cannot be negative")
        except AttributeError:
            raise serializers.ValidationError("Invalid product")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        
        if product and quantity:
            # Check if this would exceed maximum stock limit
            current_stock = product.stock
            if self.instance:
                # For updates, consider the change in quantity
                old_quantity = self.instance.quantity
                stock_change = quantity - old_quantity
                projected_stock = current_stock + stock_change
            else:
                # For new purchases
                projected_stock = current_stock + quantity
            
            if projected_stock > 1_000_000:
                raise serializers.ValidationError(
                    f"This purchase would cause stock for {product.name} to exceed maximum limit of 1,000,000"
                )
        
        return attrs

    def create(self, validated_data):
        """Create a new purchase"""
        try:
            return Purchase.objects.create(**validated_data)
        except ValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Update an existing purchase"""
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        except ValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise serializers.ValidationError(str(e))



class ExpenseSerializer(serializers.ModelSerializer):
    # Make date read-only since it's auto-generated
    date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'date']
        read_only_fields = ['date']
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_title(self, value):
        """Validate title is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
