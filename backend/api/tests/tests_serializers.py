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