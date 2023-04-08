from authentication import views
from django.urls import path

urlpatterns = [
    path('signup/', views.SignupAPIView.as_view(), name='signup'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
]
