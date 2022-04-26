from django.urls import path
# from rest_framework_jwt.views import obtain_jwt_token

from authentication.views import UserViewSet, CurrentUser

urlpatterns = [
    # path('login', obtain_jwt_token),
    path('register', UserViewSet.as_view({'post': 'create'})),
    path('users/me', CurrentUser.as_view()),
]
