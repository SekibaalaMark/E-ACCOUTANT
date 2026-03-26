from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('user-registration')  # Ensure this matches your urls.py name
        self.valid_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "customer" # Adjust based on your model's choices
        }

    def test_registration_success(self):
        """Test that a user can register with valid data."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(response.data['username'], 'testuser')
        self.assertIn('id', response.data)

    def test_registration_missing_fields(self):
        """Test that registration fails if a required field is missing."""
        invalid_payload = {"username": "incomplete_user"} # Missing email/password
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that we didn't accidentally save a user
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_registration(self):
        """Test that the view handles non-unique usernames correctly."""
        # Create an initial user
        User.objects.create_user(username="testuser", email="old@example.com", password="password")
        
        # Try to register with the same username
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data) # DRF serializers usually return the error field
        
        
        
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')  # Ensure this matches your path name
        self.password = "secure_password_123"
        self.user = User.objects.create_user(
            username="testlogin",
            email="login@example.com",
            password=self.password,
            role="admin" # Assuming your custom user model has 'role'
        )

    def test_login_success(self):
        """Test login returns tokens and user info with correct credentials."""
        data = {
            "username": "testlogin",
            "password": self.password
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify tokens exist in the response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        # Verify user data matches
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['role'], "admin")

    def test_login_invalid_password(self):
        """Test that wrong password returns 400 (or 401 depending on serializer)."""
        data = {
            "username": "testlogin",
            "password": "wrong_password"
        }
        response = self.client.post(self.url, data, format='json')

        # Since you used raise_exception=True, this will likely be 400 or 401
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('access', response.data)

    def test_login_nonexistent_user(self):
        """Test login with a username that doesn't exist."""
        data = {
            "username": "ghost_user",
            "password": "some_password"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
        




from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product

class ProductViewSetTests(APITestCase):
    def setUp(self):
        # Create an initial product for retrieval, update, and delete tests
        self.product = Product.objects.create(
            name="Gaming Mouse",
            description="High precision sensor",
            price=59.99,
            stock=10
        )
        # URLs for ViewSets usually follow this pattern:
        self.list_url = reverse('product-list') # Matches 'product-list'
        self.detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})

    def test_list_products(self):
        """Test GET /products/ returns a list."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

    def test_create_product(self):
        """Test POST /products/ creates a new record."""
        data = {
            "name": "Mechanical Keyboard",
            "description": "RGB Backlit",
            "price": 120.00,
            "stock": 5
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_retrieve_product(self):
        """Test GET /products/{id}/ returns a single record."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Gaming Mouse")

    def test_update_product(self):
        """Test PUT /products/{id}/ updates the record."""
        data = {"name": "Updated Mouse Name", "price": 65.00, "stock": 8, "description": "New description"}
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Mouse Name")

    def test_delete_product(self):
        """Test DELETE /products/{id}/ removes the record."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
        
        
        
        




from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Sale, Product

class SaleViewSetTests(APITestCase):
    def setUp(self):
        # We need a product to sell!
        self.product = Product.objects.create(
            name="Laptop",
            price=1000.00,
            stock=5
        )
        self.list_url = reverse('sale-list')

    def test_create_sale_success(self):
        """Test creating a sale updates the database and returns 201."""
        data = {
            "product": self.product.id,
            "quantity": 2,
            # 'total_price' might be calculated automatically in your model/serializer
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.count(), 1)
        
        # Verify side effects: If your Sale model reduces Product stock, check it here:
        self.product.refresh_from_db()
        # self.assertEqual(self.product.stock, 3) # Uncomment if you have stock logic

    def test_create_sale_insufficient_stock(self):
        """
        Test that a sale fails if quantity exceeds stock 
        (Assuming your serializer/model handles this validation).
        """
        data = {
            "product": self.product.id,
            "quantity": 100  # More than the 5 we have in stock
        }
        response = self.client.post(self.list_url, data, format='json')
        
        # If your logic raises a ValidationError, it should be a 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_sales(self):
        """Test retrieving all sales records."""
        # Create a dummy sale first
        Sale.objects.create(product=self.product, quantity=1)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        
        




from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Purchase, Product

class PurchaseViewSetTests(APITestCase):
    def setUp(self):
        # Initial product state
        self.product = Product.objects.create(
            name="USB-C Cable",
            price=15.00,
            stock=100
        )
        self.list_url = reverse('purchase-list')

    def test_create_purchase_increases_stock(self):
        """Test that a new purchase record correctly impacts the system."""
        data = {
            "product": self.product.id,
            "quantity": 50,
            "unit_cost": 10.00
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Purchase.objects.count(), 1)
        
        # Verify the 'select_related' logic doesn't interfere with data accuracy
        self.product.refresh_from_db()
        # If your model logic adds to stock on Purchase save:
        # self.assertEqual(self.product.stock, 150)

    def test_purchase_list_efficiency(self):
        """Verify the list view returns the correct structure."""
        Purchase.objects.create(product=self.product, quantity=10, unit_cost=10.00)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if product details are present (if your serializer nests them)
        self.assertEqual(response.data[0]['product'], self.product.id)

    def test_update_purchase_quantity(self):
        """Test updating a purchase amount."""
        purchase = Purchase.objects.create(product=self.product, quantity=10, unit_cost=10.00)
        url = reverse('purchase-detail', kwargs={'pk': purchase.pk})
        
        updated_data = {
            "product": self.product.id,
            "quantity": 20,
            "unit_cost": 10.00
        }
        response = self.client.put(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        purchase.refresh_from_db()
        self.assertEqual(purchase.quantity, 20)
        
        
        
        



from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Expense

class ExpenseViewSetTests(APITestCase):
    def setUp(self):
        # Create an initial expense for retrieval and update tests
        self.expense = Expense.objects.create(
            title="Monthly Rent",
            amount=1200.00,
            category="Utilities",
            description="Office rent for March"
        )
        self.list_url = reverse('expense-list')
        self.detail_url = reverse('expense-detail', kwargs={'pk': self.expense.pk})

    def test_create_expense(self):
        """Test POST /expenses/ creates a new expense record."""
        data = {
            "title": "Internet Bill",
            "amount": 85.50,
            "category": "Utilities"
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 2)
        self.assertEqual(Expense.objects.latest('id').title, "Internet Bill")

    def test_update_expense_amount(self):
        """Test PUT /expenses/{id}/ updates the amount correctly."""
        data = {
            "title": "Monthly Rent",
            "amount": 1300.00, # Rent increased
            "category": "Utilities"
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.amount, 1300.00)

    def test_delete_expense(self):
        """Test DELETE /expenses/{id}/ removes the record."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Expense.objects.count(), 0)

    def test_create_invalid_expense(self):
        """Test that invalid data (negative amount) is rejected."""
        data = {
            "title": "Invalid Expense",
            "amount": -50.00, # Assuming your model/serializer validates this
            "category": "Misc"
        }
        response = self.client.post(self.list_url, data, format='json')
        
        # This will test your explicit ValidationError raise in perform_create
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
        






from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

class FinancialReportsTests(APITestCase):
    def setUp(self):
        # We use a static name here; ensure this matches your router registration
        self.base_url_name = 'financial-reports' 

    def test_weekly_report_params(self):
        """Test that query parameters are correctly passed to the report."""
        url = reverse(f'{self.base_url_name}-weekly-report')
        
        # We 'mock' the service so we don't need real DB data for this specific test
        with patch('your_app.services.FinancialService.generate_financial_report') as mocked_service:
            mocked_service.return_value = {"total_sales": 500}
            
            response = self.client.get(url, {'week': 30, 'year': 2024})
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            # Verify the service was called with the converted integers
            mocked_service.assert_called_once_with('weekly', year=2024, week=30)

    def test_monthly_report_error_handling(self):
        """Test that the view handles service exceptions gracefully."""
        url = reverse(f'{self.base_url_name}-monthly-report')
        
        with patch('your_app.services.FinancialService.generate_financial_report') as mocked_service:
            # Simulate an error in the service (e.g., invalid month)
            mocked_service.side_effect = Exception("Invalid month provided")
            
            response = self.client.get(url, {'month': 13, 'year': 2024})
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error'], "Invalid month provided")

    def test_current_period_summary(self):
        """Test the combined current period report."""
        url = reverse(f'{self.base_url_name}-current-period')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('this_week', response.data['data'])
        self.assertIn('this_month', response.data['data'])
        self.assertIn('this_year', response.data['data'])
        
        
        
        




from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

class ProfitReportViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('profit-report') # Ensure this matches your urls.py name

    @patch('your_app.views.get_profit_calculations')
    def test_get_daily_profits_default(self, mock_calc):
        """Test that the view defaults to 'daily' if no period is provided."""
        mock_calc.return_value = {"profit": 100}
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_calc.assert_called_once_with('daily')
        self.assertEqual(response.data['profit'], 100)

    @patch('your_app.views.get_overall_profits')
    def test_get_overall_profits(self, mock_overall):
        """Test the branching logic for the 'overall' period."""
        mock_overall.return_value = {"total_profit": 5000}
        
        response = self.client.get(self.url, {'period': 'overall'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_overall.assert_called_once()
        self.assertEqual(response.data['total_profit'], 5000)

    @patch('your_app.views.get_profit_calculations')
    def test_invalid_period_value_error(self, mock_calc):
        """Test that a ValueError from the report helper returns a 400."""
        mock_calc.side_effect = ValueError("Invalid period specified")
        
        response = self.client.get(self.url, {'period': 'invalid_choice'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid period specified")                