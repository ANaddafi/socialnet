from rest_framework import serializers
from .models import Post, Like, Repost, Bookmark


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_reposted = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'content', 'parent',
            'created_at', 'updated_at', 'likes_count', 'comments_count', 'image', 'video', 'thumbnail',
            'reposts_count', 'shares_count', 'is_liked', 'is_bookmarked', 'is_reposted', 'comments',
            'keywords', 'tags', 'topic', 'sentiment', 'is_nsfw', 'text_to_speech_file',
            'is_toxic', 'is_offensive', 'is_blocked_by_system',
        ]

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.likes.filter(user=user).exists()

    def get_is_bookmarked(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.bookmarks.filter(user=user).exists()

    def get_is_reposted(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.reposts.filter(user=user).exists()

    def get_comments(self, obj):
        qs = obj.comments.all().order_by('-created_at')
        return PostSerializer(qs, many=True, context=self.context).data


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'parent', 'id']
        extra_kwargs = {
            'id': {'read_only': True},
            'parent': {'required': False, 'allow_null': True},
            'image': {'required': False, 'allow_null': True},
            'video': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        if attrs.get('image') and attrs.get('video'):
            raise serializers.ValidationError("A post can have either an image or a video, not both.")
        return super().validate(attrs)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['post']


class RepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = ['post']


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['post']
