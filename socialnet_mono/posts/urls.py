from django.urls import path
from .views import (
    PostCreateView, PostEditView, PostDeleteView, ProfilePostsView, PostDetailView
)


urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('profile/', ProfilePostsView.as_view(), name='profile_posts'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
]
