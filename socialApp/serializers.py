from django.db.models import Q
from rest_framework import serializers

from socialApp.models import FriendRequest, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'status')


