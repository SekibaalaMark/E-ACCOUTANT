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