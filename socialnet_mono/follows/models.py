from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following_set", on_delete=models.CASCADE)
    target = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers_set", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "target")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["target"]),
            models.Index(fields=["target", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(check=~models.Q(user=models.F("target")), name="no_self_follow")
        ]

    def clean(self):
        if self.user == self.target:
            raise ValidationError("Users cannot follow themselves.")

    def __str__(self):
        return f"{self.user.username} → {self.target.username}"
