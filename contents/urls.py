from django.urls import path, re_path

from contents.views import DeckViewSet

urlpatterns = [
    path('decks/my', DeckViewSet.as_view({
        'get': 'list',
        "post": 'create'
    })),
]
