from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import Profile
from applications.serializers import ProfileSerializer
from authentication.models import User


class CurrentUserProfileAPIView(APIView):

    @classmethod
    def get(cls, request):
        try:
            serializer = ProfileSerializer(request.user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def put(cls, request):
        try:
            serializer = ProfileSerializer(instance=request.user.profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    @classmethod
    def get(cls, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user.profile.is_private:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = ProfileSerializer(user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist or Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
