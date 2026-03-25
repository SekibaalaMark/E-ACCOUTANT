from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from decimal import Decimal  # not needed here but kept for future

User = get_user_model()


class CustomUserModelTests(TestCase):

    def test_create_user_with_default_role(self):
        """Test that a user is created with 'cashier' as default role"""
        user = User.objects.create_user(
            username="cashier1",
            email="cashier1@example.com",
            password="testpass123"
        )
        self.assertEqual(user.role, 'cashier')
        self.assertEqual(user.username, "cashier1")
        self.assertEqual(user.email, "cashier1@example.com")

    def test_create_user_with_custom_role(self):
        """Test creating users with different roles"""
        admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="testpass123",
            role='admin'
        )
        viewer = User.objects.create_user(
            username="viewer1",
            email="viewer@example.com",
            password="testpass123",
            role='viewer'
        )

        self.assertEqual(admin.role, 'admin')
        self.assertEqual(viewer.role, 'viewer')

    def test_str_method(self):
        """Test the custom __str__ method"""
        user = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="testpass123",
            role='cashier'
        )
        self.assertEqual(str(user), "john_doe (cashier)")

    def test_username_uniqueness(self):
        """Test that username must be unique"""
        User.objects.create_user(
            username="uniqueuser",
            email="user1@example.com",
            password="testpass123"
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="uniqueuser",  # duplicate username
                email="user2@example.com",
                password="testpass123"
            )

    def test_email_uniqueness(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username="userA",
            email="same@example.com",
            password="testpass123"
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="userB",
                email="same@example.com",  # duplicate email
                password="testpass123"
            )

    def test_role_choices_validation(self):
        """Test that invalid role raises error (if you add validators later)"""
        # Currently Django doesn't enforce choices at DB level unless you add constraints
        # But we can still test creating with invalid role (it will save but we can add validation later)
        user = User.objects.create_user(
            username="badrole",
            email="badrole@example.com",
            password="testpass123",
            role="invalid_role"   # not in ROLES
        )
        self.assertEqual(user.role, "invalid_role")  # currently allowed
        
        
        
        from django.test import TestCase
from django.db import IntegrityError
from decimal import Decimal
from django.contrib.auth import get_user_model

from ..models import Product, Sale   # Adjust import based on your app name

User = get_user_model()


class ProductModelTests(TestCase):

    def setUp(self):
        """Create a product and a cashier for testing"""
        self.product = Product.objects.create(
            name="Laptop Dell XPS",
            brand="Dell",
            stock=50,
            buying_price=Decimal('800.00'),
            selling_price=Decimal('1200.00')
        )

        self.cashier = User.objects.create_user(
            username="cashier1",
            email="cashier1@example.com",
            password="testpass123",
            role="cashier"
        )

    def test_product_creation(self):
        """Test basic product creation and default values"""
        self.assertEqual(self.product.name, "Laptop Dell XPS")
        self.assertEqual(self.product.brand, "Dell")
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(self.product.buying_price, Decimal('800.00'))
        self.assertEqual(self.product.selling_price, Decimal('1200.00'))
        self.assertEqual(str(self.product), "Laptop Dell XPS")

    def test_total_sales_property_no_sales(self):
        """Test total_sales when no sales exist"""
        self.assertEqual(self.product.total_sales, Decimal('0.00'))

    def test_total_sales_property_with_sales(self):
        """Test total_sales with multiple sales"""
        # Create some sales
        Sale.objects.create(
            product=self.product,
            quantity=5,
            total_price=Decimal('6000.00'),
            cashier=self.cashier
        )
        Sale.objects.create(
            product=self.product,
            quantity=3,
            total_price=Decimal('3600.00'),
            cashier=self.cashier
        )

        expected_total = Decimal('6000.00') + Decimal('3600.00')
        self.assertEqual(self.product.total_sales, expected_total)

    def test_total_profit_property_no_sales(self):
        """Test total_profit when no sales exist"""
        self.assertEqual(self.product.total_profit, Decimal('0.00'))

    def test_total_profit_property_with_sales(self):
        """Test total_profit calculation"""
        Sale.objects.create(
            product=self.product,
            quantity=10,
            total_price=Decimal('12000.00'),   # 10 * 1200
            cashier=self.cashier
        )
        Sale.objects.create(
            product=self.product,
            quantity=5,
            total_price=Decimal('6000.00'),
            cashier=self.cashier
        )

        # Profit per unit = 1200 - 800 = 400
        # Total quantity sold = 15
        expected_profit = Decimal('400.00') * 15
        self.assertEqual(self.product.total_profit, expected_profit)

    def test_total_profit_with_different_quantities(self):
        """Test profit with mixed quantities"""
        Sale.objects.create(product=self.product, quantity=2, total_price=Decimal('2400'), cashier=self.cashier)
        Sale.objects.create(product=self.product, quantity=8, total_price=Decimal('9600'), cashier=self.cashier)

        expected_profit = (Decimal('1200') - Decimal('800')) * 10   # 400 * 10
        self.assertEqual(self.product.total_profit, expected_profit)

    def test_stock_is_positive_big_integer(self):
        """Test that stock cannot be negative (thanks to PositiveBigIntegerField)"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name="Invalid Product",
                buying_price=Decimal('100'),
                selling_price=Decimal('150'),
                stock=-5   # Should raise error
            )
            
            
            
            


from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError, transaction
from decimal import Decimal
from django.contrib.auth import get_user_model

from ..models import Product, Sale, CustomUser   # adjust import if needed

User = get_user_model()


class SaleModelTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Laptop",
            brand="Dell",
            stock=20,
            buying_price=Decimal('800.00'),
            selling_price=Decimal('1200.00')
        )

        self.cashier = User.objects.create_user(
            username="cashier_test",
            email="cashier@test.com",
            password="pass123",
            role="cashier"
        )

    def test_create_sale_calculates_total_price_and_reduces_stock(self):
        """New sale: total_price should be auto-calculated and stock reduced"""
        initial_stock = self.product.stock

        sale = Sale.objects.create(
            product=self.product,
            quantity=5,
            cashier=self.cashier   # assuming you added cashier FK - if not, remove this line
        )

        self.product.refresh_from_db()

        self.assertEqual(sale.total_price, Decimal('6000.00'))        # 1200 * 5
        self.assertEqual(self.product.stock, initial_stock - 5)
        self.assertEqual(sale.quantity, 5)

    def test_quantity_must_be_positive(self):
        """Sale with quantity <= 0 should raise ValueError"""
        with self.assertRaises(ValueError) as cm:
            Sale.objects.create(
                product=self.product,
                quantity=0,
                cashier=self.cashier
            )
        self.assertIn("Quantity must be positive", str(cm.exception))

        with self.assertRaises(ValueError):
            Sale.objects.create(
                product=self.product,
                quantity=-3,
                cashier=self.cashier
            )

    def test_insufficient_stock_raises_error(self):
        """Cannot sell more than available stock"""
        with self.assertRaises(ValueError) as cm:
            Sale.objects.create(
                product=self.product,
                quantity=25,          # only 20 in stock
                cashier=self.cashier
            )
        self.assertIn("Insufficient stock", str(cm.exception))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 20)   # stock unchanged

    def test_update_sale_increase_quantity(self):
        """Increasing quantity on existing sale reduces stock further"""
        sale = Sale.objects.create(
            product=self.product,
            quantity=3,
            cashier=self.cashier
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 17)

        # Update quantity
        sale.quantity = 8
        sale.save()                     # triggers custom logic

        self.product.refresh_from_db()
        sale.refresh_from_db()

        self.assertEqual(sale.quantity, 8)
        self.assertEqual(sale.total_price, Decimal('9600.00'))   # 1200*8
        self.assertEqual(self.product.stock, 12)                 # 20 - 8 = 12

    def test_update_sale_decrease_quantity(self):
        """Decreasing quantity returns stock"""
        sale = Sale.objects.create(
            product=self.product,
            quantity=10,
            cashier=self.cashier
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

        sale.quantity = 4
        sale.save()

        self.product.refresh_from_db()
        sale.refresh_from_db()

        self.assertEqual(sale.quantity, 4)
        self.assertEqual(sale.total_price, Decimal('4800.00'))
        self.assertEqual(self.product.stock, 16)   # 20 - 4 = 16

    def test_total_sales_and_total_profit_on_product_after_sale(self):
        """Check that Product properties reflect the sale"""
        Sale.objects.create(product=self.product, quantity=5, cashier=self.cashier)
        Sale.objects.create(product=self.product, quantity=3, cashier=self.cashier)

        self.product.refresh_from_db()

        self.assertEqual(self.product.total_sales, Decimal('9600.00'))
        self.assertEqual(self.product.total_profit, Decimal('2000.00'))  # (1200-800) * 8