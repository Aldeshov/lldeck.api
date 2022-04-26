import logging

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.forms import UserCreationForm, UserChangeForm
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
    @classmethod
    def get(cls, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

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
