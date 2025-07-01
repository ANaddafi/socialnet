import pytest
from users.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username="ali", email="ali@test.com", password="1234")
    assert user.username == "ali"
    assert user.check_password("1234")
