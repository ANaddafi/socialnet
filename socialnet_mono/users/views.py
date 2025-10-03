from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from faas.interface import FaasService
from .serializers import UserSerializer, UserProfileUpdateSerializer, UserRegistrationSerializer
from .models import User


class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class ActivityReportView(APIView):
    # This view calls a FaaS function to generate an activity report for the user
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        faas = FaasService()

        from utility.report import gather_user_analytics_data
        payload = gather_user_analytics_data(user.id)
        if not payload:
            return Response({"error": "User not found or no data available"}, status=404)

        try:
            response = faas.call_function(
                function_name=faas.function_generate_report,
                payload=payload,
                is_async=False
            )
            return Response(response.json())
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        