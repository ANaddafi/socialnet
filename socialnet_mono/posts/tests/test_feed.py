import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from posts.models import Post, Like, Repost, Follow


@pytest.mark.django_db
def setup_user_and_token(client, uname, pword, email):
    user = User.objects.create_user(username=uname, password=pword, email=email)
    resp = client.post(reverse("token_obtain_pair"), {"username": uname, "password": pword}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return user


@pytest.mark.django_db
def test_feed_and_interactions():
    client = APIClient()
    user1 = setup_user_and_token(client, "ali", "pass1", "ali@x.com")
    user2 = User.objects.create_user(username="hassan", password="pass2", email="hassan@x.com")
    # user2 چند پست بسازد
    post1 = Post.objects.create(author=user2, content="post1")
    post2 = Post.objects.create(author=user2, content="post2")
    # user1 user2 را دنبال کند
    Follow.objects.create(user=user1, target=user2)
    # فید را بخواند
    resp = client.get(reverse("feed"))
    assert resp.status_code == 200
    assert len(resp.data) >= 2
    ids = [p["id"] for p in resp.data]
    assert post1.id in ids and post2.id in ids
    # لایک کند
    resp = client.post(reverse("post_like"), {"post": post1.id}, format="json")
    assert resp.status_code == 201
    # کامنت بگذارد
    resp = client.post(reverse("post_comment"), {"content": "comment1", "parent": post1.id}, format="json")
    assert resp.status_code == 201
    # ری‌پست کند
    resp = client.post(reverse("post_repost"), {"post": post1.id}, format="json")
    assert resp.status_code == 201
    # صحت شمارنده‌ها
    post1.refresh_from_db()
    assert post1.likes_count == 1
    assert post1.comments_count == 1
    assert post1.reposts_count == 1


@pytest.mark.django_db
def test_feed_follow_unfollow_behavior():
    client = APIClient()
    user1 = setup_user_and_token(client, "ali", "pass1", "ali@x.com")
    user2 = User.objects.create_user(username="hassan", password="pass2", email="hassan@x.com")
    post = Post.objects.create(author=user2, content="hello")
    # follow
    Follow.objects.create(user=user1, target=user2)
    resp = client.get(reverse("feed"))
    assert any(p["id"] == post.id for p in resp.data["results"])
    # unfollow
    Follow.objects.filter(user=user1, target=user2).delete()
    resp = client.get(reverse("feed"))
    assert all(p["id"] != post.id for p in resp.data["results"])
