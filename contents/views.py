import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from contents.helpers import ProfileCheckHelper
from contents.serializers import DeckSerializer

logger = logging.getLogger(__name__)


class DeckViewSet(viewsets.ViewSet, ProfileCheckHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated]
    serializer_class = DeckSerializer

    def get_view_name(self):
        return _("User's Decks (list & create) ViewSet")

    def get_view_description(self, html=False):
        return _("Model View set for accessing and creating deck for current request user")

    @classmethod
    def list(cls, request, *args, **kwargs):
        decks = request.user.profile.decks
        serializer = DeckSerializer(decks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @classmethod
    def create(cls, request, *args, **kwargs):
        serializer = DeckSerializer(data=request.data, context={"profile": request.user.profile})
        if serializer.is_valid():
            serializer.save()
            logger.info("User %s has created deck '%s'" % (request.user.name, serializer.data['name']))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
