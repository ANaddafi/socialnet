from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Post, Like, Repost, Bookmark
from .serializers import PostSerializer, PostCreateSerializer, LikeSerializer, RepostSerializer, BookmarkSerializer
from django.db.models import F


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostEditView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)


class ProfilePostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # if username is passed as query param, filter by that, otherwise by current user
        username = self.request.query_params.get('username')
        if username:
            return Post.objects.filter(author__username=username)
        return Post.objects.filter(author=self.request.user)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class CommentCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent')
        parent = Post.objects.filter(id=parent_id).first()
        instance = serializer.save(author=self.request.user)
        # افزایش شمارنده کامنت
        if parent:
            parent.comments_count = F('comments_count') + 1
            parent.save(update_fields=['comments_count'])


class LikePostView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        like, created = Like.objects.get_or_create(user=request.user, post_id=post_id)
        if created:
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') + 1)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)


class UnlikePostView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        like = Like.objects.filter(user=request.user, post_id=post_id).first()
        if like:
            like.delete()
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') - 1)
            return Response({'status': 'unliked'})
        return Response({'status': 'not liked'}, status=status.HTTP_404_NOT_FOUND)


class RepostView(generics.CreateAPIView):
    queryset = Repost.objects.all()
    serializer_class = RepostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        repost, created = Repost.objects.get_or_create(user=request.user, post_id=post_id)
        if created:
            Post.objects.filter(id=post_id).update(reposts_count=F('reposts_count') + 1)
            return Response({'status': 'reposted'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already reposted'}, status=status.HTTP_200_OK)


class BookmarkView(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        bm, created = Bookmark.objects.get_or_create(user=request.user, post_id=post_id)
        if created:
            return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already bookmarked'}, status=status.HTTP_200_OK)


class UnbookmarkView(generics.DestroyAPIView):
    queryset = Bookmark.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        bm = Bookmark.objects.filter(user=request.user, post_id=post_id).first()
        if bm:
            bm.delete()
            return Response({'status': 'unbookmarked'})
        return Response({'status': 'not bookmarked'}, status=status.HTTP_404_NOT_FOUND)


class BookmarkedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(bookmarks__user=self.request.user).order_by('-created_at')
