from django.db import models
from django.conf import settings


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)

    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    is_toxit = models.BooleanField(default=False)
    is_offensive = models.BooleanField(default=False)
    is_blocked_by_system = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='comments', on_delete=models.CASCADE)

    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    reposts_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    keywords = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    topic = models.CharField(max_length=100, null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~(
                    models.Q(image__isnull=False) & models.Q(video__isnull=False) &
                    ~models.Q(image='') & ~models.Q(video='')
                ),
                name='only_one_media_type'
            )
        ]


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Repost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='reposts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='bookmarks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
