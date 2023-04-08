from socialApp import views
from django.urls import path

urlpatterns = [
    path('users/', views.UserSearchAPIView.as_view(), name='search'),
    path('friend-requests/send/', views.SendFriendRequestAPIView.as_view(),
         name='send-friend-request'),
    path('friend-requests/<int:pk>/accept/',
            views.AcceptFriendRequestAPIView.as_view(), name='accept-friend-request'),
    path('friend-requests/<int:pk>/reject/',
        views.RejectFriendRequestAPIView.as_view(), name='reject-friend-request'),
    path('friends/', views.FriendListAPIView.as_view(), name='friend-list'),
    path('friend-requests/pending/', views.PendingFriendRequestListAPIView.as_view(),
            name='pending-friend-request-list'),

]
