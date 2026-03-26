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