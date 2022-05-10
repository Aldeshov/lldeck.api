import logging
import typing

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Case, When, Count, Q
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

    def popular(self):
        return self.filter(public=True).annotate(Count('downloaded')).annotate(Count('liked')) \
            .order_by('-downloaded__count', '-liked__count')

    def create_from_deck(self, deck):
        deck_template = self.create(name=deck.name, creator=deck.profile)
        deck_template.tags.set(deck.tags.all())
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
        _('Shared key'), max_length=32, validators=[MinLengthValidator(32)], null=True, unique=True, blank=True
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

    def remove_generated_shared_link(self):
        if self.shared_link_key:
            self.shared_link_key = None
            self.save()

    def like_content(self, profile, dislike=False, retract=False):
        if retract:
            self.liked.remove(profile)
            self.disliked.remove(profile)
        elif dislike:
            self.liked.remove(profile)
            self.disliked.add(profile)
        else:
            self.disliked.remove(profile)
            self.liked.add(profile)

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

    @property
    def stat_total_reviews(self):
        count = 0
        for stat in self.statistics.all():
            count += stat.total_reviews
        return count

    @property
    def stat_learned_today_count(self):
        stat = self.get_today_statistics()
        return stat.cards_learned_count if stat else 0

    @property
    def stat_seconds_gone_today(self):
        stat = self.get_today_statistics()
        return stat.seconds_gone if stat else 0

    @property
    def stat_failed_today_count(self):
        stat = self.get_today_statistics()
        return stat.cards_failed_count if stat else 0

    @property
    def stat_failed_and_not_learned_today_count(self):
        stat = self.get_today_statistics()
        return stat.cards_not_yet_learned_but_failed_count if stat else 0

    @property
    def learning_today_count(self):
        return self.cards.filter(
            opened_date__date=timezone.now().date(),
            statistics__date=None, state=CardState.STATE_GOOD
        ).count()

    def get_today_statistics(self):
        if self.statistics.last() and self.statistics.last().date == timezone.now().date():
            return self.statistics.last()

    def get_daily_new_cards(self):
        # Configuration to get daily new cards up to max count
        max_count = max(0, self.profile.aim - (
                self.stat_learned_today_count + self.learning_today_count + self.stat_failed_and_not_learned_today_count
        ))
        priority_list = [CardState.STATE_VIEWED, CardState.STATE_IDLE]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(priority_list)])

        # Getting and ordering cards
        cards = self.cards.filter(state__in=priority_list).order_by(preserved)

        # Up to max count
        if cards.count() > max_count:
            cards = cards[:max_count]

        return cards

    @property
    def daily_new_cards_count(self):
        return self.get_daily_new_cards().count()

    def get_learning_cards(self):
        return self.cards.filter(Q(state=CardState.STATE_AGAIN) | Q(statistics__date=None, state=CardState.STATE_GOOD))

    @property
    def learning_cards_count(self):
        return self.get_learning_cards().count()

    def get_to_review_cards(self):
        return self.cards.filter(state=CardState.STATE_GOOD, next_date__lte=timezone.now().date())

    @property
    def to_review_cards_count(self):
        return self.get_to_review_cards().count()

    def trigger_fail_statistics(self, card):
        self.update_statistics(card).cards_failed.add(card)

    def trigger_success_statistics(self, card):
        self.update_statistics(card).cards_learned.add(card)

    def update_statistics(self, card):
        seconds = timezone.now().timestamp() - card.opened_date.timestamp() if card and card.opened_date else 0
        stat, created = DeckDailyStatistics.objects.get_or_create(deck=self, date=timezone.now().date())
        stat.seconds_gone += seconds
        stat.save()
        return stat

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


class DeckDailyStatistics(models.Model):
    """
    Internal model class for User's deck's statistics
    Every query related deck triggered and recorded here
    """
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="statistics")

    date = models.DateField(auto_now_add=True)
    seconds_gone = models.IntegerField(default=0)
    cards_learned = models.ManyToManyField(to="contents.Card", related_name="statistics_to_cards_learned")
    cards_failed = models.ManyToManyField(to="contents.Card", related_name="statistics_to_cards_failed")

    class Meta:
        unique_together = ('deck', 'date')

    @property
    def cards_not_yet_learned_but_failed_count(self):
        return self.cards_failed.filter(~Q(id__in=self.cards_learned.all())).count()

    @property
    def cards_learned_count(self):
        return self.cards_learned.all().count()

    @property
    def cards_failed_count(self):
        return self.cards_failed.all().count()

    @property
    def total_reviews(self):
        return self.cards_learned_count + self.cards_failed_count


class Card(CardMixin):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    template = models.ForeignKey(CardTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.SmallIntegerField(choices=CardState.CARD_STATES, default=CardState.STATE_IDLE)

    opened_date = models.DateTimeField(null=True, blank=True)
    next_date = models.DateField(null=True, blank=True)
    k = models.FloatField(
        _('Coefficient of re-learning the card'), default=2.5,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )

    @property
    def success_count(self):
        return self.statistics.all().count()

    @property
    def last_success_date(self):
        if self.statistics.last():
            return self.statistics.last().date

    @property
    def is_succeeded_today(self):
        return self.statistics.last() and self.statistics.last().date == timezone.now().date()

    @property
    def is_opened_today(self):
        if self.opened_date:
            return self.opened_date.date() == timezone.now().date()

    def k_increase(self, decrease=False, commit=True):
        if decrease and self.k > 1.0:
            self.k -= 0.1
        elif not decrease and self.k < 5.0:
            self.k += 0.1

        if commit:
            self.save()

    def trigger_opened(self):
        self.opened_date = timezone.now()
        self.save()

    def perform_action_view(self):
        if self.state == CardState.STATE_IDLE and self.is_opened_today:
            self.state = CardState.STATE_VIEWED
            self.save()
            return True

    def perform_action_success(self):
        if not self.is_succeeded_today and self.is_opened_today and self.state == CardState.STATE_GOOD:
            CardSucceededStatistics.objects.get_or_create(card=self, date=timezone.now().date())
            return True
        elif self.state != CardState.STATE_IDLE:
            self.state = CardState.STATE_GOOD
            self.save()
            return True

    def perform_action_fail(self):
        if not self.is_succeeded_today and self.is_opened_today and self.state != CardState.STATE_IDLE:
            self.deck.trigger_fail_statistics(self)
            self.state = CardState.STATE_AGAIN
            self.k_increase(decrease=True, commit=False)
            self.k_increase(decrease=True, commit=False)
            self.save()
            return True


class CardSucceededStatistics(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="statistics")

    date = models.DateField(auto_now_add=True)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('card', 'date')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
            self.card.next_date = self.date + timezone.timedelta(days=int(self.card.k ** self.card.success_count))
            self.card.deck.trigger_success_statistics(self.card)
            self.card.k_increase()
        super(CardSucceededStatistics, self).save(force_insert, force_update, using, update_fields)


class CardFrontContent(CardFrontContentMixin):
    template = models.ForeignKey(CardTemplateFrontContent, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.OneToOneField(Card, related_name="front_content", on_delete=models.CASCADE)


class CardBackContent(CardBackContentMixin):
    template = models.ForeignKey(CardTemplateBackContent, on_delete=models.SET_NULL, null=True, blank=True)
    card = models.OneToOneField(Card, related_name="back_content", on_delete=models.CASCADE)
