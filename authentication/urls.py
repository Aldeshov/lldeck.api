from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from authentication.views import UserViewSet, CurrentUser

urlpatterns = [
    path('api-token/', obtain_auth_token),
    path('register/', UserViewSet.as_view({'post': 'create'})),
    path('users/me', CurrentUser.as_view()),
]
