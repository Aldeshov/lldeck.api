from rest_framework import serializers

from applications.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('id', 'user')


class ProfileStatusSerializer(serializers.ModelSerializer):
    decks_count = serializers.ReadOnlyField()
    deck_templates_count = serializers.ReadOnlyField()
    downloaded_deck_templates_count = serializers.ReadOnlyField()
    cards_learned_today = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = ('id', 'decks_count', 'deck_templates_count', 'downloaded_deck_templates_count', 'cards_learned_today')
