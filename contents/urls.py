from django.urls import path, re_path

from contents.views import (
    ProfileDeckListAPIView, PublicDeckTemplateListAPIView, NewCardListAPIView, ToReviewCardListAPIView,
    LearningCardListAPIView, ProfileDeckAPIView, CardListAPIView, CardAPIView, CardBackContentAPIView,
    CardFrontContentAPIView, CardActionAPIView, DeckTemplateListAPIView, DeckTemplateAPIView
)

urlpatterns = [
    path('decks/my', ProfileDeckListAPIView.as_view()),
    path('decks/my/<int:deck_id>', ProfileDeckAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards', CardListAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/<int:card_id>', CardAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/<int:card_id>/back', CardBackContentAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/<int:card_id>/front', CardFrontContentAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/new', NewCardListAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/learning', LearningCardListAPIView.as_view()),
    path('decks/my/<int:deck_id>/cards/to-review', ToReviewCardListAPIView.as_view()),
    path('deck-templates/my', DeckTemplateListAPIView.as_view()),
    path('deck-templates/my/<int:deck_id>', DeckTemplateAPIView.as_view()),
    path('deck-templates/popular', PublicDeckTemplateListAPIView.as_view()),
    re_path(
        r'^decks/my/(?P<deck_id>\d+)/cards/(?P<card_id>\d+)/action(?:success=(?P<success>\d+))?$',
        CardActionAPIView.as_view()
    ),
]
