"""Test user APIs."""

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

payload = {
            "email": "user@example.com",
            "password": "testpass",
            "name": "Test User"
        }

def create_user(**params):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the publicly available user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)
    
    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_too_short_error(self):
        """Test error returned if password is too short"""
        payload["password"] = "pw"
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)
    
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_token_invalid_credentials(self):
        """Test that token is not created with invalid credentials"""
        payload["password"] = "wrong"
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for user details"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

## TODO: Add tests for private user API endpoints