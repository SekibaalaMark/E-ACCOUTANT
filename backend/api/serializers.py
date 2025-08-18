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
            'brand': {'required': True}
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