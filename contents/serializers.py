from rest_framework import serializers

from contents.abstract import DeckMixin
from contents.models import DeckTag, Deck, DeckTemplate, Card, CardFrontContent, CardBackContent


class DeckTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeckTag
        fields = ("name",)


class DeckListSerializer(serializers.ModelSerializer):
    tags = DeckTagSerializer(read_only=True, many=True)
    cards_count = serializers.ReadOnlyField()

    class Meta:
        model = Deck
        fields = ('id', 'name', 'preview', 'tags', 'cards_count', 'favorite')

    def validate(self, attrs):
        raise serializers.ValidationError("Create and update not allowed")


class DeckMixinSerializer(serializers.ModelSerializer):
    cards_count = serializers.ReadOnlyField()
    date_created = serializers.ReadOnlyField()
    date_updated = serializers.ReadOnlyField()

    class Meta:
        abstract = True
        model = DeckMixin
        fields = ('id', 'name', 'preview', 'tags', 'date_created', 'date_updated', 'cards_count')


class DeckSerializer(DeckMixinSerializer):
    favorite = serializers.BooleanField(required=False)

    stat_learned_today_count = serializers.ReadOnlyField()
    stat_failed_today_count = serializers.ReadOnlyField()
    learning_today_count = serializers.ReadOnlyField()

    class Meta(DeckMixinSerializer.Meta):
        model = Deck
        fields = DeckMixinSerializer.Meta.fields + (
            'template', 'favorite', 'stat_learned_today_count', 'stat_failed_today_count', 'learning_today_count'
        )

    def validate_template(self, value):
        if value:
            if value.public or self.context.get('request').user.profile in value.shared.all():
                return value
            raise serializers.ValidationError("Invalid deck template")

    def create(self, validated_data):
        validated_data.setdefault('profile', self.context.get('request').user.profile)

        tags = validated_data.get('tags')
        if tags is not None:
            validated_data.pop('tags')

        instance = Deck.objects.create(**validated_data)

        if tags is not None:
            instance.tags.set(tags)
        return instance


class DeckTemplateListSerializer(serializers.ModelSerializer):
    cards_count = serializers.ReadOnlyField()
    downloads = serializers.ReadOnlyField()
    likes = serializers.ReadOnlyField()
    dislikes = serializers.ReadOnlyField()

    class Meta:
        model = DeckTemplate
        fields = ('id', 'name', 'cards_count', 'downloads', 'likes', 'dislikes')

    def validate(self, attrs):
        raise serializers.ValidationError("Create or update not allowed")


class CardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'name', 'state', 'front_content', 'back_content')

    def validate(self, attrs):
        raise serializers.ValidationError("Create or update not allowed")


class CardFrontContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardFrontContent
        exclude = ('template', 'card')

    def update(self, instance, validated_data):
        instance.word = validated_data.get('word') or instance.word
        instance.helper_text = validated_data.get('helper_text') or instance.helper_text
        instance.photo = validated_data.get('photo') or instance.photo
        instance.audio = validated_data.get('audio') or instance.audio
        instance.save()
        return instance


class CardBackContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardBackContent
        exclude = ('template', 'card')

    def update(self, instance, validated_data):
        instance.definition = validated_data.get('definition') or instance.definition
        instance.examples = validated_data.get('examples') or instance.examples
        instance.audio = validated_data.get('audio') or instance.audio
        instance.save()
        return instance


class CardFullSerializer(serializers.ModelSerializer):
    front_content = CardFrontContentSerializer(write_only=True)
    back_content = CardBackContentSerializer(write_only=True)

    class Meta:
        model = Card
        read_only_fields = ('state',)
        fields = ('name', 'state', 'front_content', 'back_content')

    def create(self, validated_data):
        front_content = validated_data['front_content']
        validated_data.pop('front_content')
        back_content = validated_data['back_content']
        validated_data.pop('back_content')

        validated_data.setdefault('deck', self.context['deck'])
        instance = Card.objects.create(**validated_data)

        front_content.setdefault('card', instance)
        CardFrontContent.objects.create(**front_content)

        back_content.setdefault('card', instance)
        CardBackContent.objects.create(**back_content)
        return instance


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        read_only_fields = ('template', 'state', 'front_content', 'back_content')
        fields = ('name', 'template', 'state', 'front_content', 'back_content')


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ()


class DeckTemplateSerializer(serializers.ModelSerializer):
    cards_count = serializers.ReadOnlyField()
    downloads = serializers.ReadOnlyField()
    likes = serializers.ReadOnlyField()
    dislikes = serializers.ReadOnlyField()

    class Meta:
        model = DeckTemplate
        exclude = ('creator', 'liked', 'disliked', 'downloaded')

    @classmethod
    def validate_shared_link_key(cls, value):
        return None if value == '' or not value else value

    def create(self, validated_data):
        validated_data.setdefault('creator', self.context.get('request').user.profile)

        tags = validated_data.get('tags')
        if tags is not None:
            validated_data.pop('tags')

        shared = validated_data.get('shared')
        if shared is not None:
            validated_data.pop('shared')

        instance = DeckTemplate.objects.create(**validated_data)

        if tags is not None:
            instance.tags.set(tags)

        if shared is not None:
            instance.shared.set(shared)
        return instance
