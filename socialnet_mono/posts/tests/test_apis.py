import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialnet_mono.settings_test")
django.setup()
from django.core.management import call_command
call_command("migrate", verbosity=0)

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from posts.models import Post



def create_user_and_authenticate(client, username="ali", password="pass", email="ali@test.com"):
    from django.core.management import call_command
    call_command("flush", verbosity=0, interactive=False)
    user = User.objects.create_user(username=username, password=password, email=email)
    url = reverse("token_obtain_pair")
    resp = client.post(url, {"username": username, "password": password}, format="json")
    access_token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return user


def test_post_crud_flow():
    client = APIClient()
    user = create_user_and_authenticate(client)

    # Create post
    url_create = reverse("post_create")
    resp = client.post(url_create, {"content": "First post!"}, format="json")
    assert resp.status_code == 201
    post_id = resp.data["id"] if "id" in resp.data else Post.objects.last().id

    # Edit post
    url_edit = reverse("post_edit", args=[post_id])
    resp = client.patch(url_edit, {"content": "Edited post"}, format="json")
    assert resp.status_code == 200
    assert resp.data["content"] == "Edited post"

    # View posts in profile (should contain the edited post)
    url_profile = reverse("profile_posts")
    resp = client.get(url_profile)
    assert resp.status_code == 200
    assert any(post["content"] == "Edited post" for post in resp.data)

    # View metrics for post
    url_detail = reverse("post_detail", args=[post_id])
    resp = client.get(url_detail)
    assert resp.status_code == 200
    metrics = resp.data
    assert "likes_count" in metrics and "comments_count" in metrics
    assert metrics["likes_count"] == 0

    # Delete post
    url_delete = reverse("post_delete", args=[post_id])
    resp = client.delete(url_delete)
    assert resp.status_code == 204

    # Confirm post deleted
    resp = client.get(url_detail)
    assert resp.status_code == 404


def test_post_interactions():
    client = APIClient()
    create_user_and_authenticate(client)

    # Create a post
    resp = client.post(reverse("post_create"), {"content": "hello"}, format="json")
    post_id = resp.data.get("id") or Post.objects.last().id

    # Comment on the post
    url_comment = reverse("post_comment", args=[post_id])
    resp = client.post(url_comment, {"content": "nice"}, format="json")
    assert resp.status_code == 201
    assert Post.objects.last().parent_id == post_id

    # Like the post
    url_like = reverse("post_like", args=[post_id])
    resp = client.post(url_like)
    assert resp.status_code == 200
    assert resp.data["likes_count"] == 1

    # Repost the post
    url_repost = reverse("post_repost", args=[post_id])
    resp = client.post(url_repost, {}, format="json")
    assert resp.status_code == 201
    assert Post.objects.last().repost_of_id == post_id

    # Bookmark the original post
    url_bookmark = reverse("post_bookmark", args=[post_id])
    resp = client.post(url_bookmark)
    assert resp.status_code == 200

    # View bookmarks
    url_bookmarks = reverse("bookmarks")
    resp = client.get(url_bookmarks)
    assert resp.status_code == 200
    assert any(p["id"] == post_id for p in resp.data)
