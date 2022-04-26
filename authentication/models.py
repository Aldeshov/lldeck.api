from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager
from .tools import get_user_avatar_path


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_('Full name'), max_length=128)
    email = models.EmailField(_('Email address'), unique=True)
    phone_number = PhoneNumberField(_('Phone number'), blank=True, null=True, unique=True)
    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    avatar = models.ImageField(_('Avatar'), upload_to=get_user_avatar_path, blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Is staff'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def clean(self):
        # Don't allow other users to create without phone number.
        if not self.is_superuser and not self.phone_number:
            raise ValidationError({'phone_number': _('Users must have a phone number')})

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        """
        Override default __str__ method
        :return: string value of model in format: "Name (email)"
        """
        return "%s (%s)" % (self.name, self.email)
