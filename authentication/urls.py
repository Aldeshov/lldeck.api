from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from applications.views import CurrentUserProfileAPIView, ProfileAPIView, CurrentUserProfileStatusAPIView
from authentication.views import UserViewSet, CurrentUser, UserGenericViewSet

urlpatterns = [
    path('api-token/', obtain_auth_token),
    path('register/', UserViewSet.as_view({'post': 'create'})),
    path('users/me', CurrentUser.as_view()),
    path('users/me/profile', CurrentUserProfileAPIView.as_view()),
    path('users/me/profile/status', CurrentUserProfileStatusAPIView.as_view()),
    path('users/<int:user_id>', UserGenericViewSet.as_view({'get': 'retrieve'})),
    path('users/<int:user_id>/profile', ProfileAPIView.as_view()),
]
