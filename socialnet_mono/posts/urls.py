from django.urls import path
from .views import (
    PostCreateView,
    PostEditView,
    PostDeleteView,
    ProfilePostsView,
    PostDetailView,
    PostCommentView,
    PostLikeView,
    PostRepostView,
    PostBookmarkView,
    BookmarkListView,
)


urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<int:pk>/comment/', PostCommentView.as_view(), name='post_comment'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    path('<int:pk>/repost/', PostRepostView.as_view(), name='post_repost'),
    path('<int:pk>/bookmark/', PostBookmarkView.as_view(), name='post_bookmark'),
    path('bookmarks/', BookmarkListView.as_view(), name='bookmarks'),
    path('profile/', ProfilePostsView.as_view(), name='profile_posts'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
]
