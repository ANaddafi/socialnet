import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from posts.models import Post


@pytest.mark.django_db
def create_user_and_authenticate(client, username="ali", password="pass", email="ali@test.com"):
    user = User.objects.create_user(username=username, password=password, email=email)
    url = reverse("token_obtain_pair")
    resp = client.post(url, {"username": username, "password": password}, format="json")
    access_token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return user


@pytest.mark.django_db
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
