import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from follows.models import Follow


@pytest.mark.django_db
def setup_user_and_token(client, uname, pword, email):
    user = User.objects.create_user(username=uname, password=pword, email=email)
    resp = client.post(reverse("token_obtain_pair"), {"username": uname, "password": pword}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return user


@pytest.mark.django_db
def test_follow_unfollow_and_lists():
    client = APIClient()
    user1 = setup_user_and_token(client, "ali", "pass1", "ali@x.com")
    user2 = User.objects.create_user(username="hassan", password="pass2", email="hassan@x.com")
    # Follow
    resp = client.post(reverse("follow_user"), {"target": user2.id}, format="json")
    assert resp.status_code == 201
    assert Follow.objects.filter(user=user1, target=user2).exists()
    # Double follow
    resp = client.post(reverse("follow_user"), {"target": user2.id}, format="json")
    assert resp.status_code == 200
    # Cannot follow self
    resp = client.post(reverse("follow_user"), {"target": user1.id}, format="json")
    assert resp.status_code == 400
    # Unfollow
    resp = client.delete(reverse("unfollow_user", args=[user2.id]))
    assert resp.status_code == 200
    assert not Follow.objects.filter(user=user1, target=user2).exists()
    # Unfollow again (should not exist)
    resp = client.delete(reverse("unfollow_user", args=[user2.id]))
    assert resp.status_code == 404

    # Add some more follows for list testing
    Follow.objects.create(user=user1, target=user2)
    Follow.objects.create(user=user2, target=user1)
    # user2 followers
    resp = client.get(reverse("followers_list", args=[user2.id]))
    assert resp.status_code == 200
    assert any(u['id'] == user1.id for u in resp.data)
    # user2 followings
    resp = client.get(reverse("followings_list", args=[user2.id]))
    assert resp.status_code == 200
    assert any(u['id'] == user1.id for u in resp.data)
