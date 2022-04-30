from rest_framework import serializers

from contents.abstract import DeckMixin
from contents.models import DeckTag, Deck


class DeckTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckTag
        fields = "__all__"


class DeckMixinSerializer(serializers.ModelSerializer):
    tags = DeckTagSerializer(read_only=True, many=True)
    date_created = serializers.ReadOnlyField()
    date_updated = serializers.ReadOnlyField()

    class Meta:
        abstract = True
        model = DeckMixin
        fields = ('name', 'tags', 'date_created', 'date_updated')


class DeckSerializer(DeckMixinSerializer):
    template_id = serializers.IntegerField(read_only=True)
    favorite = serializers.BooleanField(read_only=True)

    learned_today_count = serializers.ReadOnlyField()
    failed_today_count = serializers.ReadOnlyField()
    learning_today_count = serializers.ReadOnlyField()

    class Meta(DeckMixinSerializer.Meta):
        model = Deck
        fields = DeckMixinSerializer.Meta.fields + (
            'template_id', 'favorite', 'learned_today_count', 'failed_today_count', 'learning_today_count'
        )

    def create(self, validated_data):
        validated_data.setdefault('profile', self.context.get('profile'))
        validated_data.setdefault('template', self.context.get('template'))
        return Deck.objects.create(**validated_data)
