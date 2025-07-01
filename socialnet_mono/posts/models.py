from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE,
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relations
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    repost_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="reposts",
        on_delete=models.CASCADE,
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
    )
    bookmarked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="bookmarked_posts",
        blank=True,
    )

    # Metrics fields
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    reposts_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

