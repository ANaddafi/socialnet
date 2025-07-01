import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialnet_mono.settings_test")
django.setup()
from django.core.management import call_command
call_command("migrate", verbosity=0)

from users.serializers import UserSerializer
from users.models import User


def test_user_serializer():
    user = User(username="bob", email="bob@example.com", bio="Hi")
    data = UserSerializer(user).data
    assert data["username"] == "bob"
    assert data["bio"] == "Hi"
