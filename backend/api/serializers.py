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

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

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