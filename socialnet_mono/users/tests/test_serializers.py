from users.serializers import UserSerializer
from users.models import User


def test_user_serializer():
    user = User(username="bob", email="bob@example.com", bio="Hi")
    data = UserSerializer(user).data
    assert data["username"] == "bob"
    assert data["bio"] == "Hi"
