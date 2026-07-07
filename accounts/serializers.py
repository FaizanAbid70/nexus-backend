import uuid
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, StartupHistory, InvestmentHistory


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        # Frontend never sends a username, so we generate a unique one
        # behind the scenes from the email (Django's User model still needs one internally).
        base_username = validated_data['email'].split('@')[0]
        username = f"{base_username}_{uuid.uuid4().hex[:6]}"

        return User.objects.create_user(
            username=username,
            name=validated_data.get('name', ''),
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user_obj = User.objects.get(email__iexact=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password')

        # authenticate() checks against USERNAME_FIELD (still 'username' internally),
        # so we look the user up by email first, then authenticate using their real username.
        user = authenticate(username=user_obj.username, password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password')

        data['user'] = user
        return data
class StartupHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupHistory
        fields = '__all__'
        read_only_fields = ['user']


class InvestmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentHistory
        fields = '__all__'
        read_only_fields = ['user']


class ProfileSerializer(serializers.ModelSerializer):
    startup_history = StartupHistorySerializer(many=True, read_only=True)
    investment_history = InvestmentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'username', 'email', 'role', 'bio',
            'profile_picture', 'preferences',
            'startup_history', 'investment_history'
        ]
class PublicProfileSerializer(serializers.ModelSerializer):
    startup_history = StartupHistorySerializer(many=True, read_only=True)
    investment_history = InvestmentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'username', 'role', 'bio',
            'profile_picture', 'startup_history', 'investment_history'
        ]