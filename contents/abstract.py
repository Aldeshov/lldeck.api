import typing

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from contents.tools import get_card_content_path
from lldeck.settings import DECK_TAG_MODEL


class DeckMixin(models.Model):
    """
    Abstract Base class of Deck model
    """
    name = models.CharField(_('Name'), max_length=128, default="<Unnamed deck>")
    tags = models.ManyToManyField(
        to=DECK_TAG_MODEL,
        related_name="%(class)s_list",
        help_text="Deck TAGs, used to sort by special tags."
    )
    date_created = models.DateTimeField(_('Date created'), auto_now_add=True)

    cards = typing.Any  # related_name

    class Meta:
        abstract = True

    @property
    def short_date_created(self):
        if self.date_created:
            return self.date_created.date()

    def __str__(self):
        return "%s (from %s)" % (self.name, self.short_date_created)

    @property
    def cards_count(self):
        return len(self.cards.all())


class CardMixin(models.Model):
    """
    Abstract Base class of Card model
    Must have Relation with Deck model
    """
    name = models.CharField(_('Name'), max_length=128, default="<Unnamed card>")
    deck = models.ForeignKey(DeckMixin, related_name="cards", on_delete=models.CASCADE)

    front_content = typing.Any  # related_name
    back_content = typing.Any  # related_name

    class Meta:
        abstract = True

    def __str__(self):
        return "%s from deck '%s'" % (self.name, self.deck.name)


class CardFrontContentMixin(models.Model):
    """
    Abstract Base class of Card's front content model
    Must have Relation with Card model
    """
    word = models.CharField(max_length=128)
    helper_text = models.CharField(max_length=128, null=True, blank=True)
    photo = models.ImageField(_('Image file'), upload_to=get_card_content_path, null=True, blank=True)
    audio = models.FileField(_('Audio file'), upload_to=get_card_content_path, null=True, blank=True)
    card = models.OneToOneField(CardMixin, related_name="front_content", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return "Front of card '%s'" % self.card.name


class CardBackContentMixin(models.Model):
    """
    Abstract Base class of Card's back content model
    Must have Relation with Card model
    """
    definition = models.TextField(_('Definition'))
    examples = ArrayField(models.CharField(max_length=128), size=8, default=list, blank=True)
    audio = models.FileField(_('Audio file'), upload_to=get_card_content_path, null=True, blank=True)
    card = models.OneToOneField(CardMixin, related_name="back_content", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return "Back of card '%s'" % self.card.name
