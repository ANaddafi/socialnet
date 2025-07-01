from rest_framework import serializers
from .models import Follow
from users.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'bio', 'avatar']


class FollowSerializer(serializers.ModelSerializer):
    target = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['target']
