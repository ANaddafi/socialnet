from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Post, Like, Repost, Bookmark
from .serializers import PostSerializer, PostCreateSerializer, LikeSerializer, RepostSerializer, BookmarkSerializer
from django.db.models import F

User = get_user_model()


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostEditView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)


class ProfilePostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        target = get_object_or_404(User.objects, pk=self.kwargs['pk'])
        return Post.objects.filter(author=target)

class MyPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent')
        parent = get_object_or_404(Post.objects, pk=parent_id)
        instance = serializer.save(author=self.request.user)
        if parent:
            parent.comments_count = F('comments_count') + 1
            parent.save(update_fields=['comments_count'])
        return instance


class LikePostView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        post = get_object_or_404(Post.objects, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') + 1)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)


class UnlikePostView(generics.DestroyAPIView):
    queryset = Like.objects.all()

    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post.objects, pk=post_id)
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') - 1)
            return Response({'status': 'unliked'})
        return Response({'status': 'not liked'}, status=status.HTTP_404_NOT_FOUND)


class RepostView(generics.CreateAPIView):
    queryset = Repost.objects.all()
    serializer_class = RepostSerializer

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        post = get_object_or_404(Post.objects, pk=post_id)
        repost, created = Repost.objects.get_or_create(user=request.user, post=post)
        if created:
            Post.objects.filter(id=post_id).update(reposts_count=F('reposts_count') + 1)
            return Response({'status': 'reposted'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already reposted'}, status=status.HTTP_200_OK)


class BookmarkView(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

    def create(self, request, *args, **kwargs):
        post_id = request.data['post']
        post = get_object_or_404(Post.objects, pk=post_id)
        bm, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already bookmarked'}, status=status.HTTP_200_OK)


class UnbookmarkView(generics.DestroyAPIView):
    queryset = Bookmark.objects.all()

    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post.objects, pk=post_id)
        bm = Bookmark.objects.filter(user=request.user, post=post).first()
        if bm:
            bm.delete()
            return Response({'status': 'unbookmarked'})
        return Response({'status': 'not bookmarked'}, status=status.HTTP_404_NOT_FOUND)


class BookmarkedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(bookmarks__user=self.request.user).order_by('-created_at')


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        # TODO: also include reposts
        following_ids = self.request.user.following_set.values_list('target_id', flat=True)
        return Post.objects.filter(
            author_id__in=list(following_ids) + [self.request.user.id],
            parent=None,  # swap out comments
        ).order_by('-created_at')
