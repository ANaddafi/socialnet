import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from posts.models import Post, Like, Bookmark, Repost


@pytest.mark.django_db
def user_and_auth(client, name="user", passw="pass", mail="mail@test.com"):
    u = User.objects.create_user(username=name, password=passw, email=mail)
    resp = client.post(reverse("token_obtain_pair"), {"username": name, "password": passw}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return u


@pytest.mark.django_db
def test_comment_like_repost_bookmark_flow():
    client = APIClient()
    user = user_and_auth(client)
    # create a post
    resp = client.post(reverse("post_create"), {"content": "original"}, format="json")
    post_id = resp.data["id"]

    # comment (comment is a post with parent=post_id)
    resp = client.post(reverse("post_comment"), {"content": "a comment", "parent": post_id}, format="json")
    assert resp.status_code == 201
    assert Post.objects.filter(parent_id=post_id).count() == 1

    # like post
    resp = client.post(reverse("post_like"), {"post": post_id}, format="json")
    assert resp.status_code == 201
    assert Like.objects.filter(post_id=post_id, user=user).exists()

    # unlike post
    resp = client.delete(reverse("post_unlike", args=[post_id]))
    assert resp.status_code == 200
    assert not Like.objects.filter(post_id=post_id, user=user).exists()

    # repost
    resp = client.post(reverse("post_repost"), {"post": post_id}, format="json")
    assert resp.status_code == 201
    assert Repost.objects.filter(post_id=post_id, user=user).exists()

    # bookmark
    resp = client.post(reverse("post_bookmark"), {"post": post_id}, format="json")
    assert resp.status_code == 201
    assert Bookmark.objects.filter(post_id=post_id, user=user).exists()

    # unbookmark
    resp = client.delete(reverse("post_unbookmark", args=[post_id]))
    assert resp.status_code == 200
    assert not Bookmark.objects.filter(post_id=post_id, user=user).exists()

    # see bookmarked posts (should be empty now)
    resp = client.get(reverse("bookmarked_posts"))
    assert resp.status_code == 200
    assert resp.data == []
