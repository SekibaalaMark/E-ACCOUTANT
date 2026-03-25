from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError
from decimal import Decimal

from ..serializers import UserRegistrationSerializer
from ..models import CustomUser


class UserRegistrationSerializerTests(TestCase):

    def test_valid_registration_data(self):
        """Test serializer with correct data"""
        data = {
            'username': 'johncashier',
            'email': 'john@example.com',
            'role': 'cashier',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.username, 'johncashier')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.role, 'cashier')
        self.assertTrue(user.check_password('SecurePass123'))
        self.assertFalse(user.has_usable_password()) is False  # password is hashed

    def test_passwords_must_match(self):
        """Test validation when passwords don't match"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'viewer',
            'password': 'password123',
            'confirm_password': 'wrongpassword'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Passwords do not match")

    def test_password_min_length(self):
        """Test password minimum length validation"""
        data = {
            'username': 'shortpass',
            'email': 'short@example.com',
            'role': 'cashier',
            'password': '12345',           # only 5 characters
            'confirm_password': '12345'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_confirm_password_min_length(self):
        """Test confirm_password also respects min_length"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'admin',
            'password': 'longpassword123',
            'confirm_password': '123'      # too short
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('confirm_password', serializer.errors)

    def test_role_is_optional_and_defaults_to_cashier(self):
        """Role should default to 'cashier' if not provided (from model)"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
            # role intentionally omitted
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.role, 'cashier')

    def test_invalid_role_choice(self):
        """Invalid role should fail validation (because of model choices)"""
        data = {
            'username': 'badrole',
            'email': 'badrole@example.com',
            'role': 'superadmin',           # not in ROLES
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_username_and_email_uniqueness(self):
        """Test uniqueness constraints from CustomUser model"""
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )

        data = {
            'username': 'existinguser',          # duplicate username
            'email': 'newemail@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

        # Test duplicate email
        data2 = {
            'username': 'anotheruser',
            'email': 'existing@example.com',     # duplicate email
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }

        serializer2 = UserRegistrationSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertIn('email', serializer2.errors)

    def test_create_method_removes_confirm_password(self):
        """confirm_password should be popped and not saved"""
        data = {
            'username': 'cleanuser',
            'email': 'clean@example.com',
            'role': 'viewer',
            'password': 'MyPass123',
            'confirm_password': 'MyPass123'
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # confirm_password should not exist on the model
        self.assertFalse(hasattr(user, 'confirm_password'))
        
        
        




from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib.auth import get_user_model

from ..serializers import LoginSerializer

User = get_user_model()


class LoginSerializerTests(TestCase):

    def setUp(self):
        """Create test users"""
        self.active_user = User.objects.create_user(
            username="cashier1",
            email="cashier1@example.com",
            password="CorrectPass123",
            role="cashier"
        )

        self.inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="Pass123",
            role="viewer"
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def test_valid_login_returns_tokens_and_role(self):
        """Successful login should return access + refresh tokens + role"""
        data = {
            "username": "cashier1",
            "password": "CorrectPass123"
        }

        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data

        self.assertIn("access", validated_data)
        self.assertIn("refresh", validated_data)
        self.assertIn("role", validated_data)
        self.assertEqual(validated_data["username"], "cashier1")
        self.assertEqual(validated_data["role"], "cashier")

        # Tokens should be non-empty strings
        self.assertIsInstance(validated_data["access"], str)
        self.assertIsInstance(validated_data["refresh"], str)
        self.assertGreater(len(validated_data["access"]), 20)
        self.assertGreater(len(validated_data["refresh"]), 20)

    def test_invalid_credentials_raises_error(self):
        """Wrong password or non-existent user should fail"""
        # Wrong password
        data = {
            "username": "cashier1",
            "password": "WrongPassword123"
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0], "Invalid username or password.")

        # Non-existent username
        data2 = {
            "username": "ghostuser",
            "password": "anything"
        }
        serializer2 = LoginSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertEqual(serializer2.errors["non_field_errors"][0], "Invalid username or password.")

    def test_empty_username_or_password(self):
        """Username and password are required"""
        # Missing username
        serializer = LoginSerializer(data={"password": "pass123"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

        # Missing password
        serializer = LoginSerializer(data={"username": "cashier1"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_inactive_user_login(self):
        """Test login behavior for inactive users"""
        data = {
            "username": "inactive",
            "password": "Pass123"
        }

        serializer = LoginSerializer(data=data)

        # Currently your code allows inactive users (the check is commented out)
        # So this should pass
        self.assertTrue(serializer.is_valid())

        # Uncomment the block below if you later enable the is_active check:
        # with self.assertRaises(DRFValidationError):
        #     serializer.is_valid(raise_exception=True)

    def test_login_returns_correct_role(self):
        """Make sure the role is correctly returned for different user types"""
        admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="AdminPass123",
            role="admin"
        )

        data = {"username": "admin1", "password": "AdminPass123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["role"], "admin")

    def test_authenticate_uses_django_backend(self):
        """Ensure authenticate() is actually being used (integration test)"""
        # This test indirectly verifies that authenticate() works with CustomUser
        data = {
            "username": "cashier1",
            "password": "CorrectPass123"
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # If we reach here, authenticate() succeeded
        
        







from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError
from decimal import Decimal

from ..serializers import ProductSerializer
from ..models import Product


class ProductSerializerTests(TestCase):

    def test_valid_product_data(self):
        """Test serializer with completely valid data"""
        data = {
            'name': 'Dell XPS 15',
            'brand': 'Dell',
            'stock': 25,
            'buying_price': Decimal('850.00'),
            'selling_price': Decimal('1250.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertEqual(validated_data['name'], 'Dell XPS 15')
        self.assertEqual(validated_data['brand'], 'Dell')
        self.assertEqual(validated_data['stock'], 25)
        self.assertEqual(validated_data['buying_price'], Decimal('850.00'))
        self.assertEqual(validated_data['selling_price'], Decimal('1250.00'))

    def test_name_cannot_be_empty_or_whitespace(self):
        """Test custom validation: name cannot be empty"""
        data = {
            'name': '   ',                    # only whitespace
            'brand': 'HP',
            'stock': 10,
            'buying_price': Decimal('500.00'),
            'selling_price': Decimal('700.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertEqual(serializer.errors['name'][0], "Product name cannot be empty.")

    def test_buying_price_cannot_be_negative(self):
        """Test buying_price validation"""
        data = {
            'name': 'Invalid Product',
            'brand': 'Test',
            'stock': 5,
            'buying_price': Decimal('-10.00'),
            'selling_price': Decimal('100.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('buying_price', serializer.errors)
        self.assertEqual(serializer.errors['buying_price'][0], "Buying price cannot be negative.")

    def test_selling_price_cannot_be_negative(self):
        """Test selling_price validation"""
        data = {
            'name': 'Invalid Product',
            'brand': 'Test',
            'stock': 5,
            'buying_price': Decimal('100.00'),
            'selling_price': Decimal('-50.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('selling_price', serializer.errors)

    def test_selling_price_must_be_greater_or_equal_to_buying_price(self):
        """Business rule: selling price >= buying price"""
        data = {
            'name': 'Loss Making Product',
            'brand': 'Test',
            'stock': 10,
            'buying_price': Decimal('1000.00'),
            'selling_price': Decimal('900.00')      # selling < buying
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('selling_price', serializer.errors)
        self.assertEqual(
            serializer.errors['selling_price'][0],
            "Selling price should not be less than buying price."
        )

    def test_stock_cannot_be_negative(self):
        """Test stock validation (even though model prevents it)"""
        data = {
            'name': 'Negative Stock',
            'brand': 'Test',
            'stock': -5,
            'buying_price': Decimal('200.00'),
            'selling_price': Decimal('300.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock', serializer.errors)

    def test_brand_is_required(self):
        """brand is marked as required in extra_kwargs"""
        data = {
            'name': 'No Brand Product',
            'stock': 10,
            'buying_price': Decimal('100.00'),
            'selling_price': Decimal('150.00')
            # brand intentionally omitted
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('brand', serializer.errors)

    def test_stock_is_required(self):
        """stock is marked as required in extra_kwargs"""
        data = {
            'name': 'No Stock Info',
            'brand': 'Test',
            'buying_price': Decimal('100.00'),
            'selling_price': Decimal('150.00')
            # stock intentionally omitted
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock', serializer.errors)

    def test_id_is_read_only(self):
        """id should be read-only and ignored on create/update"""
        data = {
            'id': 999,                          # trying to set id
            'name': 'Test Product',
            'brand': 'Test',
            'stock': 10,
            'buying_price': Decimal('100.00'),
            'selling_price': Decimal('150.00')
        }

        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())   # should still be valid
        self.assertNotIn('id', serializer.validated_data)  # id should be stripped

    def test_serializer_can_update_existing_product(self):
        """Test that serializer works correctly on update"""
        product = Product.objects.create(
            name="Old Laptop",
            brand="HP",
            stock=15,
            buying_price=Decimal('700.00'),
            selling_price=Decimal('900.00')
        )

        update_data = {
            'name': 'Updated Laptop',
            'brand': 'Dell',
            'stock': 30,
            'buying_price': Decimal('800.00'),
            'selling_price': Decimal('1100.00')
        }

        serializer = ProductSerializer(instance=product, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_product = serializer.save()

        self.assertEqual(updated_product.name, 'Updated Laptop')
        self.assertEqual(updated_product.stock, 30)
        self.assertEqual(updated_product.selling_price, Decimal('1100.00'))
        
        
        


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
    





from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError
from decimal import Decimal

from ..serializers import PurchaseSerializer
from ..models import Product, Purchase


class PurchaseSerializerTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Smartphone",
            brand="Samsung",
            stock=100,
            buying_price=Decimal('650.00'),
            selling_price=Decimal('950.00')
        )

        self.product2 = Product.objects.create(
            name="Second Product",
            brand="Xiaomi",
            stock=50,
            buying_price=Decimal('300.00'),
            selling_price=Decimal('450.00')
        )

    # ====================== Basic Validation Tests ======================

    def test_valid_purchase_data(self):
        """Valid data should pass all validations"""
        data = {
            'product': self.product.id,
            'quantity': 25,
        }

        serializer = PurchaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated = serializer.validated_data
        self.assertEqual(validated['product'], self.product)
        self.assertEqual(validated['quantity'], 25)

    def test_quantity_must_be_positive(self):
        """Test custom validate_quantity method"""
        data = {
            'product': self.product.id,
            'quantity': 0,
        }
        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)
        self.assertEqual(serializer.errors['quantity'][0], "Quantity must be positive")

        data['quantity'] = -10
        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_product_must_have_valid_buying_price(self):
        """Test validate_product method"""
        bad_product = Product.objects.create(
            name="Bad Product",
            brand="Test",
            stock=10,
            buying_price=Decimal('-50.00'),   # negative buying price
            selling_price=Decimal('100.00')
        )

        data = {
            'product': bad_product.id,
            'quantity': 5,
        }

        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product', serializer.errors)
        self.assertEqual(serializer.errors['product'][0], "Product buying price cannot be negative")

    def test_projected_stock_max_limit_on_create(self):
        """Test maximum stock limit validation on new purchase"""
        self.product.stock = 999_990
        self.product.save()

        data = {
            'product': self.product.id,
            'quantity': 20,          # would make stock 1,000,010 > 1_000_000
        }

        serializer = PurchaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn("exceed maximum limit of 1,000,000", serializer.errors['non_field_errors'][0])

    # ====================== Creation Tests ======================

    def test_create_purchase_calculates_total_cost_and_increases_stock(self):
        """Serializer create should trigger model's save() logic"""
        initial_stock = self.product.stock

        data = {
            'product': self.product.id,
            'quantity': 40,
        }

        serializer = PurchaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        purchase = serializer.save()

        self.product.refresh_from_db()

        self.assertEqual(purchase.quantity, 40)
        self.assertEqual(purchase.total_cost, Decimal('26000.00'))   # 650 * 40
        self.assertEqual(self.product.stock, initial_stock + 40)

    # ====================== Update Tests ======================

    def test_update_quantity_increases_stock(self):
        """Increasing quantity should increase stock"""
        purchase = Purchase.objects.create(product=self.product, quantity=10)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 110)

        update_data = {'quantity': 35}

        serializer = PurchaseSerializer(instance=purchase, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_purchase = serializer.save()
        self.product.refresh_from_db()

        self.assertEqual(updated_purchase.quantity, 35)
        self.assertEqual(updated_purchase.total_cost, Decimal('22750.00'))
        self.assertEqual(self.product.stock, 135)   # 100 + 35 = 135

    def test_update_quantity_decreases_stock(self):
        """Decreasing quantity should reduce stock"""
        purchase = Purchase.objects.create(product=self.product, quantity=60)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 160)

        update_data = {'quantity': 20}

        serializer = PurchaseSerializer(instance=purchase, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 120)   # 100 + 20 = 120

    def test_changing_product_on_update(self):
        """Changing product should adjust stock on both products"""
        purchase = Purchase.objects.create(product=self.product, quantity=30)  # stock1 = 130

        update_data = {
            'product': self.product2.id,
            'quantity': 15
        }

        serializer = PurchaseSerializer(instance=purchase, data=update_data)
        self.assertTrue(serializer.is_valid())

        serializer.save()

        self.product.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product.stock, 100)      # reverted 30
        self.assertEqual(self.product2.stock, 65)      # 50 + 15 = 65

    def test_update_respects_max_stock_limit(self):
        """Update should also respect max stock limit"""
        self.product.stock = 999_980
        self.product.save()

        purchase = Purchase.objects.create(product=self.product, quantity=5)

        update_data = {'quantity': 50}   # would exceed limit

        serializer = PurchaseSerializer(instance=purchase, data=update_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("exceed maximum limit", str(serializer.errors))

    # ====================== Read-only & Extra Fields ======================

    def test_extra_read_only_fields(self):
        """product_name and product_buying_price should appear in output"""
        purchase = Purchase.objects.create(product=self.product, quantity=10)

        serializer = PurchaseSerializer(purchase)
        data = serializer.data

        self.assertEqual(data['product_name'], "Test Smartphone")
        self.assertEqual(data['product_buying_price'], "650.00")
        self.assertIn('total_cost', data)
        self.assertIn('date', data)        