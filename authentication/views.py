from typing import Union

#django
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
# rest_framework
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

#custom
from authentication.models import User
from authentication.serializers import LoginSerializer
from socialApp.models import FriendRequest, UserStatus
from socialApp.serializers import UserSerializer


class SignupAPIView(generics.CreateAPIView):

    """
        Signup User
    """
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        name = serializer.validated_data['name']
        password = serializer.validated_data['password']

        # get or create a object with email
        user, created = User.objects.get_or_create(email=email)
        if created:
            # call a method for saving additional field
            response = self.data_creation(user, password, name)
            return Response(response, status=status.HTTP_201_CREATED)

        # Create a error response
        response = {
            "status": False,
            "message": "Email already exists",
            "data": []
        }
        
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    
    def data_creation(self, user, password, name):
        user.set_password(password)
        user.name = name
        user.save()
        data = [{'email': user.email, 'user_id': user.id}]
        return {
                "status": True,
                "message": "User created successfully",
                "data": data
        }
     

class LoginAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    login_serializer_class = LoginSerializer

    def post(self, request, format=None):
        """
            Login User
        """

        serializer = self.login_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)


        user = serializer.login()
        # if user not exists return response
        if user is False:
            response = {
                "status": False,
                "message": "User  does not exist",
                "data": []
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # get user token
        token = RefreshToken.for_user(user)

        jwt_access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        jwt_refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        data = {
            "refresh": str(token),
            "access": str(token.access_token),
            "access_token_life_time_in_seconds": jwt_access_token_lifetime.total_seconds(),
            "refresh_token_life_time_in_seconds": jwt_refresh_token_lifetime.total_seconds(),
        }

        # Create a success response with the serialized data
        response = {
            "status": True,
            "message": "User Log In successfully",
            "data": [data]
        }

        return Response(response, status=status.HTTP_200_OK)


