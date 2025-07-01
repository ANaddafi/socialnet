import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialnet_mono.settings_test")
django.setup()
from django.core.management import call_command
call_command("migrate", verbosity=0)

import pytest
from users.models import User


def test_create_user():
    from django.core.management import call_command
    call_command("flush", verbosity=0, interactive=False)
    user = User.objects.create_user(username="ali", email="ali@test.com", password="1234")
    assert user.username == "ali"
    assert user.check_password("1234")
