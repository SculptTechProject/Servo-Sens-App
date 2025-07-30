"""Test user APIs."""

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

payload = {"email": "user@example.com", "password": "testpass", "name": "Test User"}


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
        short_pw_payload = {**payload, "password": "pw"}
        res = self.client.post(CREATE_USER_URL, short_pw_payload)
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
        create_user(email=payload["email"], password="testpass", name=payload["name"])
        bad_payload = {"email": payload["email"], "password": "pw"}
        res = self.client.post(TOKEN_URL, bad_payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for user details"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test the authorized user API"""

    def setUp(self):
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"email": self.user.email, "name": self.user.name})

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {"name": "New Name", "password": "newpassword"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
