from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import SimpleRateThrottle
from rest_framework import generics, permissions, status

from socialApp.serializers import (FriendRequestSerializer,UserSerializer)
from socialApp.models import FriendRequest, User, UserStatus

class FriendRequestThrottle(SimpleRateThrottle):
    """
        Throttle class for limiting request per minute
    """
    scope = 'friend_request'

    def get_cache_key(self, request, view):
        # Throttle based on user ID
        return f"{self.get_ident(request)}"

    def allow_request(self, request, view):
        # Allow 3 requests per minute
        self.rate = '3/minute'
        return super().allow_request(request, view)


class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
            Queryset for search user
        """

        search_term = self.request.query_params.get('search', '').strip()

        # if @ is in search then it's email
        if '@' in search_term:
            return User.objects.filter(email__iexact=search_term)
        else:
            return User.objects.filter(name__icontains=search_term)

    def get(self, request, *args, **kwargs):
        """
            List of search user
        """

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        # if page exists then return response
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # Create a success response with the serialized data
        response = {
            "status": True,
            "message": "User fetched successfully",
            "data": [serializer.data]
        }

        return Response(response, status=status.HTTP_200_OK)


class SendFriendRequestAPIView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    throttle_classes = [FriendRequestThrottle]

    def create(self, request, *args, **kwargs):
        """
            Send friend request to user
        """

        sender = request.user
        receiver_id = request.data.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)

        # check if receiver_id is exists if not then return response
        if not receiver_id:
            return Response(
                {
                    "status": False,
                    "Message": 'Receiver ID is required.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if sender and receiver both are same then return response
        if int(sender.id) == int(receiver_id):
            return Response(
                {
                    "status": False,
                    "Message": 'You cannot send a friend request to yourself.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there is an active friend request between the sender and the receiver
        if existing_request := FriendRequest.objects.filter(
            sender=sender, receiver=receiver, status=UserStatus.SEND
        ).first():
            return Response(
                {
                    "status": False,
                    "Message": 'You already sent a friend request to this user.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check if the receiver already sent a friend request to the sender
        if reverse_request := FriendRequest.objects.filter(
                sender=receiver, receiver=sender, status=UserStatus.SEND).first():
            # If the receiver already sent a friend request, accept it and return success response
            reverse_request.status = UserStatus.ACCEPT
            reverse_request.save()
            return Response(
                {
                    "status": False,
                    "Message": 'Friend request accepted successfully.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )
        friend_requests = FriendRequest.objects.filter(
            sender_id=sender.id, created_at__gte=timezone.now() - timezone.timedelta(minutes=1)).count()

        # Create the FriendRequest object with the sender and receiver IDs
        friend_request = FriendRequest.objects.create(
            sender=sender, receiver_id=receiver_id)

        # Set the status of the friend request to "SEND"
        friend_request.status = UserStatus.SEND
        friend_request.save()

        serializer = self.get_serializer(friend_request)

        return Response(serializer.data)


class RejectFriendRequestAPIView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        """
            Reject friend request
        """

        friend_request = self.get_object()
        if friend_request.receiver != self.request.user:
            # If the user is not authorized to reject this friend request, return an unauthorized response
            return Response(
                {
                    "status": False,
                    "Message": 'You are not authorized to update this friend request.',
                    "data": []

                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        if friend_request.status != UserStatus.SEND:
            # if the user has already accepted or declined the request
            return Response(
                {
                    "status": False,
                    "Message": 'Friend request is already accepted or declined.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            friend_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Create a success response with the serialized data
        response = {
            "status": True,
            "Message": 'Friend request rejected successfully.',
            "data": serializer.data
        }
        return Response(
            response,
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        serializer.save(status=UserStatus.REJECT)


class AcceptFriendRequestAPIView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        """
           Accept friend request
        """

        friend_request = self.get_object()
        if friend_request.receiver != self.request.user:
            # If the user is not authorized to reject this friend request, return an unauthorized response
            return Response(
                {
                    "status": False,
                    "Message": 'You are not authorized to update this friend request.',
                    "data": []

                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        if friend_request.status != UserStatus.SEND:
            # if the user has already accepted or declined the request
            return Response(
                {
                    "status": False,
                    "Message": 'Friend request is already accepted or declined.',
                    "data": []

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            friend_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Create a success response with the serialized data
        response = {
            "status": True,
            "Message": 'Friend request accepted successfully.',
            "data": serializer.data
        }
        return Response(
            response,
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        serializer.save(status=UserStatus.ACCEPT)


class FriendListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        """
            Queryset for list of friends
        """

        user = self.request.user
        friend_ids = list(FriendRequest.objects.filter(
            sender=user, status=UserStatus.ACCEPT).values_list('receiver_id', flat=True))
        friend_ids = list(FriendRequest.objects.filter(
            receiver=user, status=UserStatus.ACCEPT).values_list('sender_id', flat=True))
        return User.objects.filter(id__in=friend_ids)

    def get(self, request):
        """
            list friends 
        """

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        if len(serializer.data) > 0:
            # Create a success response with the serialized data
            response = {
                "status": True,
                "Message": 'Your friends list fetched successfully.',
                "data": serializer.data
            }
        else:
            response = {
                "status": False,
                "Message": 'You don\'t have friend.',
                "data": serializer.data
            }
        return Response(response, status=status.HTTP_200_OK)


class PendingFriendRequestListAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        """
            Queryset for get pending request
        """
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, status=UserStatus.SEND)

    def get(self, request):
        """
            List pending friend request
        """

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        if len(serializer.data) > 0:
            # Create a success response with the serialized data
            response = {
                "status": True,
                "Message": 'Your pending friends list fetched successfully.',
                "data": serializer.data
            }
        else:
            response = {
                "status": False,
                "Message": 'You don\'t have pending friend request.',
                "data": serializer.data
            }
        return Response(response, status=status.HTTP_200_OK)


