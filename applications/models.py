import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.constants import Theme, ProfileStatus, UserLanguage
from lldeck.settings import AUTH_USER_MODEL


class Profile(models.Model):
    is_private = models.BooleanField(
        _('Is private'),
        default=True,
        help_text=_("Designates whether this user profile is private. Private profiles invisible to others")
    )
    user = models.OneToOneField(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    aim = models.IntegerField(_('Aim'), default=100, help_text="Count of card to learn every day")
    about = models.CharField(_('About'), max_length=256, blank=True, default="Hey there! I am learning on ll-deck!")
    status = models.SmallIntegerField(
        _('Status'),
        choices=ProfileStatus.PROFILE_STATUSES,
        default=ProfileStatus.PROFILE_IDLE
    )
    selected_theme_mode = models.SmallIntegerField(_('Theme mode'), choices=Theme.THEME_MODES, default=Theme.THEME_IDLE)
    selected_language = models.SmallIntegerField(
        _('Language'),
        choices=UserLanguage.PROFILE_LANGUAGES,
        default=UserLanguage.LANGUAGE_NONE
    )

    decks = typing.Any  # related_name
    deck_templates = typing.Any  # related_name
    shared_deck_templates = typing.Any  # related_name
    downloaded_deck_templates = typing.Any  # related_name

    # followed = models.ManyToManyField(to=PROFILE_MODEL, related_name='followers', blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'All Users Profiles'

    @property
    def decks_count(self):
        return len(self.decks.all())

    @property
    def deck_templates_count(self):
        return len(self.deck_templates.all())

    @property
    def downloaded_deck_templates_count(self):
        return len(self.downloaded_deck_templates.all())

    @property
    def cards_learned_today(self):
        return

    def __str__(self):
        return "%s's profile" % self.user.name
