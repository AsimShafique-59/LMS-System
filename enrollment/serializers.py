from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model



def get_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)

class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'department', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        role = validated_data.get('role')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if role == 'student':
            Student.objects.create(user=user)
        elif role == 'teacher':
            Staff.objects.create(user=user)  # Or Teacher if renamed

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh, access = get_jwt_token(instance)
        return {
            'refresh': refresh,
            'access': access,
            'user': data
        }

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'department', 'role']

    def create(self, validated_data):
        role = validated_data.get("role")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create related profile based on role
        if role == "student":
            Student.objects.create(user=user)
        elif role == "teacher":
            Teacher.objects.create(user=user)  # Use Teacher, not Staff

        return user

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'department', 'role']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
