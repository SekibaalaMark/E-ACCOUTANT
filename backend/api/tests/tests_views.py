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