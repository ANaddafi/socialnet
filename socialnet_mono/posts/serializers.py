from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'content',
            'created_at', 'updated_at',
            'likes_count', 'comments_count', 'reposts_count', 'shares_count'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at',
                            'likes_count', 'comments_count', 'reposts_count', 'shares_count']


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content']
