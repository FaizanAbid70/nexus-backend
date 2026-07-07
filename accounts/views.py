from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer,
    ProfileSerializer, PublicProfileSerializer
)



@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    return Response({"status": "ok"})


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': ProfileSerializer(user).data,
            'tokens': get_tokens_for_user(user)
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            'user': ProfileSerializer(user).data,
            'tokens': get_tokens_for_user(user)
        })
    
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return Response(PublicProfileSerializer(user).data)


class UserListView(APIView):
    """
    GET /api/auth/users/?role=investor
    Lists other users (optionally filtered by role) so the frontend can pick
    someone to invite to a meeting or view in the Investors/Entrepreneurs pages.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = User.objects.exclude(id=request.user.id)
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return Response(PublicProfileSerializer(queryset, many=True).data)