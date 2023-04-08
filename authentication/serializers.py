from django.db.models import Q
from rest_framework import serializers

from authentication.models import User
from socialApp.models import FriendRequest, UserStatus


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def login(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']

        user = User.objects.filter(Q(email=email))

        if user.exists():
            if user[0].check_password(password):
                return user[0]
        else:
            return False

