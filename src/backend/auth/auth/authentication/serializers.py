from django.db.models.base import ModelBase
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from UserModel.models import User
from typing import List
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class UserSerializerRegister(serializers.ModelSerializer):
    username: serializers.CharField = serializers.CharField(
        required=True,
        max_length=50,
        min_length=5,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        help_text="Username must be unique and have a length between 5 and 50 characters.",
    )

    password: serializers.CharField = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        max_length=50,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        help_text="Password must have a length between 8 and 50 characters.",
    )

    email: serializers.EmailField = serializers.EmailField(
        required=True, help_text="Email must be unique."
    )

    nickname: serializers.CharField = serializers.CharField(
        required=True,
        min_length=3,
        max_length=50,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="Nickname must have a length between 3 and 50 characters.",
    )

    class Meta:
        model: ModelBase = User
        fields: List = ["username", "password", "email", "nickname", "avatar"]

    def create(self, validated_data) -> User | serializers.ValidationError:
        username = validated_data.get('username')
        if User.objects.filter(username=username):
                raise serializers.ValidationError({"username": "Username already in use."})
        nickname = validated_data.get('nickname')
        if User.objects.filter(nickname=nickname):
                raise serializers.ValidationError({"nickname": "nickname already in use."})
        email = validated_data.get('email')
        if User.objects.filter(email=email):
            raise serializers.ValidationError({"email": "email already in use."})

        user: User = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            ip=self.context["request"].META.get("REMOTE_ADDR"),
            ip_last_login=self.context["request"].META.get("REMOTE_ADDR"),
            nickname=validated_data.get("nickname"),
            avatar=validated_data.get("avatar", 'avatars/pepe.png'),
        )
        return user


class UserSerializer(serializers.Serializer):
    username: serializers.CharField = serializers.CharField(
        required=True,
        max_length=50,
        min_length=5,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
    )
    password: serializers.CharField = serializers.CharField(
        required=True,
    )

    def validate(self, attrs) -> User:
        user: User = authenticate(
            username=attrs.get("username"), password=attrs.get("password")
        )
        if user is not None and user.is_active:
            user.ip_last_login = self.context["request"].META.get(
                "REMOTE_ADDR")
            user.status = True
            user.save()
            return user
        raise serializers.ValidationError("Incorrect Credentials")


""" class TokenVerifySerializer(serializers.Serializer):
    token: serializers.CharField = serializers.CharField(required=True)

    def validate(self, attrs) -> dict:
        return attrs """

class UserDataSerializer(serializers.Serializer):
    newUsername: serializers.CharField = serializers.CharField(required=True)
    newNickname: serializers.CharField = serializers.CharField(required=True)
    newEmail: serializers.CharField = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user

        newUsername = attrs.get('newUsername')
        if newUsername:
            if User.objects.filter(username=newUsername).exclude(id=user.id).exists():
                raise serializers.ValidationError({"username": "Username already in use."})

        newNickname = attrs.get('newNickname')
        if newNickname:
            if User.objects.filter(nickname=newNickname).exclude(id=user.id).exists():
                raise serializers.ValidationError({"nickname": "Nickname already in use."})

        newEmail = attrs.get('newEmail')
        if newEmail:
            if User.objects.filter(email=newEmail).exclude(id=user.id).exists():
                raise serializers.ValidationError({"email": "Email already in use."})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user

        user.username = self.validated_data.get('newUsername', user.username)
        user.nickname = self.validated_data.get('newNickname', user.nickname)
        user.email = self.validated_data.get('newEmail', user.email)
        
        user.save()
        return user

class PasswdSerializer(serializers.Serializer):
    currentPassword: serializers.CharField = serializers.CharField(required=True)
    newPassword: serializers.CharField = serializers.CharField(required=True)
    confirmPassword: serializers.CharField = serializers.CharField(required=True)

    class Meta:
        model: ModelBase = User
        fields: List = ["currentPasswd", "newPasswd", "confirmPasswd"]

    def validate(self, attrs):
        #
        print(attrs)
        user = self.context['request'].user
        print(self.context['request'])

        # Obtener los campos de la solicitud
        current_password = attrs.get('currentPassword')
        new_password = attrs.get('newPassword')
        confirm_password = attrs.get('confirmPassword')

        # Validar que todos los campos estén presentes
        if not current_password or not new_password or not confirm_password:
            raise serializers.ValidationError({"error": "All fields need to be validate."})

        # Verificar que la contraseña actual sea correcta
        if not check_password(current_password, user.password):
            raise serializers.ValidationError({"currentPassword": "Current password is incorrect."})

        # Verificar que la nueva contraseña y su confirmación coincidan
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirmPassword": "The two password fields didn’t match."})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['newPassword']
        user.password = make_password(new_password)
        user.save()
        return user