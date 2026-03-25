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