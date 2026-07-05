from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, StartupHistory, InvestmentHistory


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
        )
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid username or password')
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
            'id', 'username', 'email', 'role', 'bio',
            'profile_picture', 'preferences',
            'startup_history', 'investment_history'
        ]
class PublicProfileSerializer(serializers.ModelSerializer):
    startup_history = StartupHistorySerializer(many=True, read_only=True)
    investment_history = InvestmentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'role', 'bio',
            'profile_picture', 'startup_history', 'investment_history'
        ]