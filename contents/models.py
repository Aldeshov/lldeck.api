import logging
import typing

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from contents.abstract import DeckMixin, CardMixin, CardBackContentMixin, CardFrontContentMixin
from contents.constants import CardState
from contents.tools import random_string
from contents.validators import validate_tag_name
from lldeck.settings import PROFILE_MODEL

logger = logging.getLogger(__name__)


class TagField(models.CharField):
    default_validators = [validate_tag_name]

    def __init__(self, *args, **kwargs):
        super(TagField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


class DeckTag(models.Model):
    """
    Base class model for Deck TAGs
    """
    name = TagField(_("name"), max_length=16, unique=True)

    deck_list = typing.Any  # related_name
    decktemplate_list = typing.Any  # related_name

    class Meta:
        verbose_name = _("Deck #TAG")
        verbose_name_plural = _("Deck TAGs")

    def __str__(self):
        return "[TAG] %s" % self.name


class DeckTemplateManager(models.Manager):
    """
    Deck Template Manager allows creating templates from existing decks
    * Moved from managers.py due to circular import
    """

    def create_from_deck(self, deck):
        deck_template = self.create(name=deck.name, creator=deck.profile, tags=deck.tags)
        for card in deck.cards.all() or []:
            card_template = CardTemplate.objects.create(name=card.name, deck=deck_template)
            try:
                CardTemplateFrontContent.objects.create(
                    word=card.front_content.word,
                    helper_text=card.helper_text,
                    photo=ImageFile(
                        ContentFile(
                            card.front_content.photo.read(),
                            card.front_content.photo.name)
                    ) if card.front_content.photo else card.front_content.photo,
                    audio=ContentFile(
                        card.front_content.audio.read(),
                        card.front_content.audio.name
                    ) if card.front_content.audio else card.front_content.audio,
                    card=card_template
                )
                CardTemplateBackContent.objects.create(
                    definition=card.back_content.definition,
                    examples=card.back_content.examples,
                    audio=ContentFile(
                        card.back_content.audio.read(),
                        card.back_content.audio.name
                    ) if card.back_content.audio else card.back_content.audio,
                    card=card_template
                )
            except Card.front_content.RelatedObjectDoesNotExist or Card.back_content.RelatedObjectDoesNotExist as error:
                logger.error(error)
        return deck_template


class DeckTemplate(DeckMixin):
    """
    Deck Template model used to create other decks using this template
    Owner of this deck (creator) required field
    """
    creator = models.ForeignKey(to=PROFILE_MODEL, on_delete=models.CASCADE, related_name="deck_templates")
    shared = models.ManyToManyField(to=PROFILE_MODEL, related_name="shared_deck_templates", blank=True)
    shared_link_key = models.CharField(
        _('Shared key'), max_length=32, validators=[MinLengthValidator(32)], null=True, unique=True
    )
    public = models.BooleanField(default=False, help_text="Designates whether this deck template is public.")

    liked = models.ManyToManyField(to=PROFILE_MODEL, related_name="liked_deck_templates")
    disliked = models.ManyToManyField(to=PROFILE_MODEL, related_name="disliked_deck_templates")
    downloaded = models.ManyToManyField(to=PROFILE_MODEL, related_name="downloaded_deck_templates")

    objects = DeckTemplateManager()

    def generate_shared_link_key(self):
        key = random_string()
        while DeckTemplate.objects.filter(shared_link_key=key).exists():
            key = random_string()
        self.shared_link_key = key
        self.save()

    @property
    def downloads(self):
        return self.downloaded.all().count()

    @property
    def likes(self):
        return self.liked.all().count()

    @property
    def dislikes(self):
        return self.disliked.all().count()


class CardTemplate(CardMixin):
    """
    Card Template model used to create other decks' cards using this template
    Deck of this card required is field
    """
    deck = models.ForeignKey(DeckTemplate, on_delete=models.CASCADE, related_name="cards")

    def __str__(self):
        return "%s from template deck '%s'" % (self.name, self.deck.name)


class CardTemplateFrontContent(CardFrontContentMixin):
    """
    Card Template's Front content model used to create other cards' front content using this template
    Card of this content is required field
    """
    card = models.OneToOneField(CardTemplate, related_name="front_content", on_delete=models.CASCADE)

    def __str__(self):
        return "Front of card template '%s'" % self.card.name


class CardTemplateBackContent(CardBackContentMixin):
    """
    Card Template's Back content model used to create other cards' back content using this template
    Card of this content is required field
    """
    card = models.OneToOneField(CardTemplate, related_name="back_content", on_delete=models.CASCADE)

    def __str__(self):
        return "Back of card template '%s'" % self.card.name


class Deck(DeckMixin):
    template = models.ForeignKey(
        DeckTemplate, on_delete=models.SET_NULL,
        help_text="To import from existing templates",
        null=True, blank=True
    )
    favorite = models.BooleanField(default=False)
    profile = models.ForeignKey(to=PROFILE_MODEL, on_delete=models.CASCADE, related_name="decks")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, use_template=False):
        if self.template and not self.pk:
            use_template = True

        super(Deck, self).save(force_insert, force_update, using, update_fields)

        if use_template:
            self.tags.set(self.template.tags.all())
            self.template.downloaded.add(self.profile)
            for card_template in self.template.cards.all() or []:
                card = Card.objects.create(name=card_template.name, template=card_template, deck=self)
                try:
                    CardFrontContent.objects.create(
                        template=card_template.front_content,
                        word=card_template.front_content.word,
                        helper_text=card_template.front_content.helper_text,
                        photo=ImageFile(
                            ContentFile(
                                card_template.front_content.photo.read(),
                                card_template.front_content.photo.name
                            )
                        ) if card_template.front_content.photo else card_template.front_content.photo,
                        audio=ContentFile(
                            card_template.front_content.audio.read(),
                            card_template.front_content.audio.name
                        ) if card_template.front_content.audio else card_template.front_content.audio,
                        card=card
                    )
                    CardBackContent.objects.create(
                        template=card_template.back_content,
                        definition=card_template.back_content.definition,
                        examples=card_template.back_content.examples,
                        audio=ContentFile(
                            card_template.back_content.audio.read(),
                            card_template.back_content.audio.name
                        ) if card_template.back_content.audio else card_template.back_content.audio,
                        card=card
                    )
                except CardTemplate.front_content.RelatedObjectDoesNotExist as error:
                    logger.error(error)
                except CardTemplate.back_content.RelatedObjectDoesNotExist as error:
                    logger.error(error)


class Card(CardMixin):
    template = models.ForeignKey(CardTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    state = models.SmallIntegerField(choices=CardState.CARD_STATES, default=CardState.STATE_IDLE)

    succeeded_date = models.DateTimeField(null=True, blank=True)

    def perform_action_view(self):
        if self.state == CardState.STATE_IDLE:
            self.state = CardState.STATE_VIEWED
            self.save()

    def perform_action_success(self):
        not_today = not self.succeeded_date or self.succeeded_date.date() != timezone.now().date()
        if not_today and self.state == CardState.STATE_GOOD:
            self.succeeded_date = timezone.now()
            self.save()
        elif self.state != CardState.STATE_GOOD:
            self.state = CardState.STATE_GOOD
            self.save()

    def perform_action_fail(self):
        if self.state != CardState.STATE_AGAIN:
            self.state = CardState.STATE_AGAIN
            self.save()


class CardFrontContent(CardFrontContentMixin):
    template = models.ForeignKey(CardTemplateFrontContent, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.OneToOneField(Card, related_name="front_content", on_delete=models.CASCADE)


class CardBackContent(CardBackContentMixin):
    template = models.ForeignKey(CardTemplateBackContent, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.OneToOneField(Card, related_name="back_content", on_delete=models.CASCADE)
