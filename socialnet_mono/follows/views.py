from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Follow
from users.models import User
from .serializers import FollowSerializer, UserPublicSerializer


class FollowUserView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        target_id = request.data.get("target")
        if int(target_id) == request.user.id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(user=request.user, target_id=target_id)
        if created:
            return Response({"status": "followed"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already following"}, status=status.HTTP_200_OK)


class UnfollowUserView(generics.DestroyAPIView):
    queryset = Follow.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        target_id = kwargs.get("target_id")
        deleted, _ = Follow.objects.filter(user=request.user, target_id=target_id).delete()
        if deleted:
            return Response({"status": "unfollowed"})
        return Response({"status": "not following"}, status=status.HTTP_404_NOT_FOUND)


class FollowersListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return User.objects.filter(following_set__target_id=user_id)


class FollowingsListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return User.objects.filter(followers_set__user_id=user_id)
