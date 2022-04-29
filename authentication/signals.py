import logging

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from applications.models import Profile
from authentication.models import User
from .tools import delete_file


@receiver(post_save, sender=User)
def user_created(sender: User, **kwargs):
    if kwargs.get("created"):
        Profile.objects.create(user_id=kwargs.get("instance").id)


@receiver(post_delete, sender=User)
def user_deleted(sender: User, **kwargs):
    if kwargs.get("instance").avatar:
        delete_file(kwargs.get("instance").avatar)


@receiver(pre_save, sender=User)
def user_changed(sender: User, **kwargs):
    try:
        previous = sender.objects.get(id=kwargs.get("instance").id)
        if previous.avatar != kwargs.get("instance").avatar:
            delete_file(previous.avatar)
    except sender.DoesNotExist as error:
        logging.debug(error)
