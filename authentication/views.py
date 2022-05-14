import logging

from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.forms import UserCreationForm, UserChangeForm, LoginForm
from authentication.models import User
from authentication.serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @classmethod
    def create(cls, request):
        form = UserCreationForm(data=request.data)
        if form.is_valid():
            instance = form.save()
            serializer = UserSerializer(instance)
            logger.info("User '%s' has been created" % instance.name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUser(APIView):
    def check_permissions(self, request):
        if request.method != 'POST' and not request.user.is_authenticated:
            self.permission_denied(
                request,
                message=getattr(AllowAny, 'message', None),
                code=getattr(AllowAny, 'code', None)
            )

    @classmethod
    def get(cls, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @classmethod
    def post(cls, request):
        if request.data.get("logout") and request.user.is_authenticated:
            name = request.user.name
            logout(request)
            logger.info("User '%s' logged out" % name)
            return Response(status=status.HTTP_200_OK)

        form = LoginForm(request, data=request.POST or request.data)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                logger.info("User '%s' logged in" % user.name)
                if not remember_me:
                    request.session.set_expiry(0)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"message": "The given credentials are not valid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def put(cls, request):
        if request.data.get("old_password"):
            form = PasswordChangeForm(request.user, request.data)
            if form.is_valid():
                instance = form.save()
                update_session_auth_hash(request, instance)  # Important!
                logger.info("User '%s' changed password" % request.user.name)
                return Response(form.data, status=status.HTTP_200_OK)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        form = UserChangeForm(instance=request.user, data=request.data)
        if form.is_valid():
            instance = form.save()
            serializer = UserSerializer(instance)
            logger.info("User '%s' has been updated" % request.user.name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def delete(cls, request):
        name = request.user.name
        request.user.delete()
        logger.info("User '%s' has been deleted" % name)
        return Response(status=status.HTTP_200_OK)


class UserGenericViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)

    @classmethod
    def retrieve(cls, request, user_id):
        if User.objects.filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
