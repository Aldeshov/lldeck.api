import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from contents.filters import DeckTemplateFilter, DeckFilter
from contents.helpers import ProfileCheckHelper, ProfileDeckGetHelper, ProfileDeckCardGetHelper
from contents.models import DeckTemplate
from contents.serializers import DeckSerializer, DeckTemplateListSerializer, CardListSerializer, DeckListSerializer, \
    CardFullSerializer, CardSerializer, CardFrontContentSerializer, CardBackContentSerializer, ActionSerializer, \
    DeckTemplateSerializer

logger = logging.getLogger(__name__)


class ProfileDeckListAPIView(generics.ListCreateAPIView, ProfileCheckHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = (DjangoFilterBackend,)
    filter_class = DeckFilter

    def get_queryset(self):
        return self.request.user.profile.decks.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DeckListSerializer
        return DeckSerializer


class PublicDeckTemplateListAPIView(generics.ListAPIView):
    queryset = DeckTemplate.objects.popular()
    serializer_class = DeckTemplateListSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = DeckTemplateFilter


class ProfileDeckAPIView(generics.RetrieveUpdateDestroyAPIView, ProfileCheckHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = DeckSerializer

    def get_queryset(self):
        return self.request.user.profile.decks.all()

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {'id': self.kwargs.get('deck_id')}
        deck = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, deck)
        return deck


class CardListAPIView(generics.ListCreateAPIView, ProfileCheckHelper, ProfileDeckGetHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        deck = self.deck(self)
        self.check_object_permissions(self.request, deck)
        return deck.cards.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CardListSerializer
        return CardFullSerializer

    def get_serializer_context(self):
        context = super(CardListAPIView, self).get_serializer_context()
        context.setdefault('deck', self.deck(self))
        return context


class CardAPIView(generics.RetrieveUpdateDestroyAPIView, ProfileCheckHelper, ProfileDeckCardGetHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CardSerializer

    def get_object(self):
        card = self.card(self)
        self.check_object_permissions(self.request, card)
        return card


class CardActionAPIView(generics.UpdateAPIView, ProfileCheckHelper, ProfileDeckCardGetHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ActionSerializer

    def get_object(self):
        card = self.card(self)
        self.check_object_permissions(self.request, card)
        return card

    def put(self, request, *args, **kwargs):
        card = self.get_object()
        if str(request.query_params.get('success')).isnumeric():
            if int(request.query_params.get('success')) > 0:
                card.perform_action_success()
                logger.info("User '%s' performed action <success> to the card '%s'" % (self.request.user.name, card))
                return Response({"action": "success"}, status=status.HTTP_200_OK)
            card.perform_action_fail()
            logger.info("User '%s' performed action <fail> to the card '%s'" % (self.request.user.name, card))
            return Response({"action": "fail"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CardFrontContentAPIView(generics.RetrieveUpdateAPIView, ProfileCheckHelper, ProfileDeckCardGetHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CardFrontContentSerializer

    def get_object(self):
        card = self.card(self)
        self.check_object_permissions(self.request, card)
        return card.front_content

    def retrieve(self, request, *args, **kwargs):
        result = super(CardFrontContentAPIView, self).retrieve(request, *args, **kwargs)
        logger.info("User '%s' <opened> the card '%s'" % (self.request.user.name, self.get_object().card))
        card = self.get_object().card
        card.trigger_opened()
        return result


class CardBackContentAPIView(generics.RetrieveUpdateAPIView, ProfileCheckHelper, ProfileDeckCardGetHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = CardBackContentSerializer

    def get_object(self):
        card = self.card(self)
        self.check_object_permissions(self.request, card)
        return card.back_content

    def retrieve(self, request, *args, **kwargs):
        result = super(CardBackContentAPIView, self).retrieve(request, *args, **kwargs)
        logger.info("User '%s' <viewed> the card '%s'" % (self.request.user.name, self.get_object().card))
        card = self.get_object().card
        card.perform_action_view()
        return result


class NewCardListAPIView(generics.ListAPIView, ProfileDeckGetHelper):
    serializer_class = CardListSerializer

    def get_queryset(self):
        deck = self.deck(self)
        self.check_object_permissions(self.request, deck)
        return deck.get_daily_new_cards()


class LearningCardListAPIView(generics.ListAPIView, ProfileDeckGetHelper):
    serializer_class = CardListSerializer

    def get_queryset(self):
        deck = self.deck(self)
        self.check_object_permissions(self.request, deck)
        return deck.get_learning_cards()


class ToReviewCardListAPIView(generics.ListAPIView, ProfileDeckGetHelper):
    serializer_class = CardListSerializer

    def get_queryset(self):
        deck = self.deck(self)
        self.check_object_permissions(self.request, deck)
        return deck.get_to_review_cards()


class DeckTemplateListAPIView(generics.ListCreateAPIView, ProfileCheckHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return self.request.user.profile.deck_templates.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DeckTemplateListSerializer
        return DeckTemplateSerializer


class DeckTemplateAPIView(generics.RetrieveUpdateDestroyAPIView, ProfileCheckHelper):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return DeckTemplateSerializer

    def get_queryset(self):
        return self.request.user.profile.deck_templates.all()

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {'id': self.kwargs.get('deck_id')}
        deck_template = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, deck_template)
        return deck_template
