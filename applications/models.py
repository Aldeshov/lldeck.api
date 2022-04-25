from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.constants import Theme, ProfileStatus, UserLanguage


class Profile(models.Model):
    is_private = models.BooleanField(_('Is private'), default=True)
    aim = models.CharField(_('Aim'), max_length=128, blank=True, default="")
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
    # subscribed = models.ManyToManyField(User, related_name='channel_subscribers', blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'All Users Profiles'
