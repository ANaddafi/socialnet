from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Follow
from .serializers import FollowSerializer, UserPublicSerializer

User = get_user_model()


class FollowUserView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        target_id = kwargs.get("target_id")
        if target_id is None:
            return Response({"error": "target_id is required in URL."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_id_int = int(target_id)
        except (TypeError, ValueError):
            return Response({"error": "invalid target_id."}, status=status.HTTP_400_BAD_REQUEST)
        if target_id_int == request.user.id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        target_user = get_object_or_404(User, pk=target_id_int)
        follow, created = Follow.objects.get_or_create(user=request.user, target=target_user)
        if created:
            return Response({"status": "followed"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already following"}, status=status.HTTP_200_OK)


class UnfollowUserView(generics.DestroyAPIView):
    queryset = Follow.objects.all()

    def delete(self, request, *args, **kwargs):
        target_id = kwargs.get("target_id")
        if target_id is None:
            return Response({"error": "target_id is required in URL."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_id_int = int(target_id)
        except (TypeError, ValueError):
            return Response({"error": "invalid target_id."}, status=status.HTTP_400_BAD_REQUEST)
        target_user = get_object_or_404(User, pk=target_id_int)
        deleted, _ = Follow.objects.filter(user=request.user, target=target_user).delete()
        if deleted:
            return Response({"status": "unfollowed"})
        return Response({"status": "not following"}, status=status.HTTP_404_NOT_FOUND)


class FollowersListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        target_id = self.kwargs.get("target_id")
        if target_id is None:
            return User.objects.none()
        try:
            target_id_int = int(target_id)
        except (TypeError, ValueError):
            return User.objects.none()
        target_user = get_object_or_404(User, pk=target_id_int)
        return User.objects.filter(following_set__target=target_user)


class FollowingsListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        target_id = self.kwargs.get("target_id")
        if target_id is None:
            return User.objects.none()
        try:
            target_id_int = int(target_id)
        except (TypeError, ValueError):
            return User.objects.none()
        target_user = get_object_or_404(User, pk=target_id_int)
        return User.objects.filter(followers_set__user=target_user)
