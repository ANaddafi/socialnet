from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import F
from .models import Post
from .serializers import PostSerializer, PostCreateSerializer


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


class PostCommentView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parent_post = Post.objects.get(pk=self.kwargs["pk"])
        parent_post.comments_count = F("comments_count") + 1
        parent_post.save(update_fields=["comments_count"])
        serializer.save(author=self.request.user, parent=parent_post)


class PostLikeView(generics.GenericAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        if user in post.liked_by.all():
            post.liked_by.remove(user)
            post.likes_count = F("likes_count") - 1
        else:
            post.liked_by.add(user)
            post.likes_count = F("likes_count") + 1
        post.save(update_fields=["likes_count"])
        post.refresh_from_db(fields=["likes_count"])
        return Response({"likes_count": post.likes_count})


class PostRepostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        original = self.get_object()
        original.reposts_count = F("reposts_count") + 1
        original.save(update_fields=["reposts_count"])
        serializer.save(
            author=self.request.user,
            content=original.content,
            repost_of=original,
        )


class PostBookmarkView(generics.GenericAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        if user in post.bookmarked_by.all():
            post.bookmarked_by.remove(user)
        else:
            post.bookmarked_by.add(user)
        return Response(status=status.HTTP_200_OK)


class BookmarkListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(bookmarked_by=self.request.user)
