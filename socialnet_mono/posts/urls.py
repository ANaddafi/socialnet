from django.urls import path
from .views import (
    PostCreateView, PostEditView, PostDeleteView, ProfilePostsView, PostDetailView,
    CommentCreateView, LikePostView, UnlikePostView, RepostView,
    BookmarkView, UnbookmarkView, BookmarkedPostsView, FeedView,
)


urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('profile/', ProfilePostsView.as_view(), name='profile_posts'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('comment/', CommentCreateView.as_view(), name='post_comment'),
    path('like/', LikePostView.as_view(), name='post_like'),
    path('unlike/<int:post_id>/', UnlikePostView.as_view(), name='post_unlike'),
    path('repost/', RepostView.as_view(), name='post_repost'),
    path('bookmark/', BookmarkView.as_view(), name='post_bookmark'),
    path('unbookmark/<int:post_id>/', UnbookmarkView.as_view(), name='post_unbookmark'),
    path('bookmarked/', BookmarkedPostsView.as_view(), name='bookmarked_posts'),
    path('feed/', FeedView.as_view(), name='feed'),
]
