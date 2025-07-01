from django.urls import path
from .views import FollowUserView, UnfollowUserView, FollowersListView, FollowingsListView

urlpatterns = [
    path('follow/', FollowUserView.as_view(), name='follow_user'),
    path('unfollow/<int:target_id>/', UnfollowUserView.as_view(), name='unfollow_user'),
    path('<int:user_id>/followers/', FollowersListView.as_view(), name='followers_list'),
    path('<int:user_id>/followings/', FollowingsListView.as_view(), name='followings_list'),
]
