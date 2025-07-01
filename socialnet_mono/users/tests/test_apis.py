import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialnet_mono.settings_test")
django.setup()
from django.core.management import call_command
call_command("migrate", verbosity=0)

import tempfile
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
import pytest


def test_register_login_and_profile_flow():
    from django.core.management import call_command
    call_command("flush", verbosity=0, interactive=False)
    client = APIClient()

    # Register user
    url_register = reverse("register")
    register_data = {
        "username": "john",
        "password": "testpass123",
        "email": "john@example.com"
    }
    resp = client.post(url_register, register_data, format="json")
    assert resp.status_code == 201
    assert resp.data["username"] == "john"

    # Login user
    url_token = reverse("token_obtain_pair")
    login_data = {
        "username": "john",
        "password": "testpass123"
    }
    resp = client.post(url_token, login_data, format="json")
    assert resp.status_code == 200
    access_token = resp.data["access"]

    # View profile
    url_profile = reverse("profile")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    resp = client.get(url_profile)
    assert resp.status_code == 200
    assert resp.data["username"] == "john"

    # Edit profile (text field)
    url_edit = reverse("profile_edit")
    edit_data = {"bio": "new bio!"}
    resp = client.patch(url_edit, edit_data, format="json")
    assert resp.status_code == 200
    assert resp.data["bio"] == "new bio!"

    # Edit profile (avatar image)
    with tempfile.NamedTemporaryFile(suffix=".jpg") as img:
        img.write(b"fakeimgdata")
        img.seek(0)
        resp = client.patch(url_edit, {"avatar": img}, format="multipart")
        assert resp.status_code == 200
        assert "avatar" in resp.data
