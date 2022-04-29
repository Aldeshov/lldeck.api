import logging

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import CardFrontContent, CardTemplateFrontContent, CardTemplateBackContent, CardBackContent
from .tools import delete_file, delete_empty_dirs, delete_old_files


@receiver(post_delete, sender=CardFrontContent)
@receiver(post_delete, sender=CardTemplateFrontContent)
def front_content_deleted(sender, **kwargs):
    if kwargs.get("instance").photo:
        delete_file(kwargs.get("instance").photo)
        delete_empty_dirs(kwargs.get("instance").photo.path)
    if kwargs.get("instance").audio:
        delete_file(kwargs.get("instance").audio)
        delete_empty_dirs(kwargs.get("instance").audio.path)


@receiver(post_delete, sender=CardBackContent)
@receiver(post_delete, sender=CardTemplateBackContent)
def back_content_deleted(sender, **kwargs):
    if kwargs.get("instance").audio:
        delete_file(kwargs.get("instance").audio)
        delete_empty_dirs(kwargs.get("instance").audio.path)


@receiver(pre_save, sender=CardFrontContent)
@receiver(pre_save, sender=CardTemplateFrontContent)
def front_content_changed(sender, **kwargs):
    try:
        previous = sender.objects.get(id=kwargs.get("instance").id)
        delete_old_files(previous.photo, kwargs.get("instance").photo)
        delete_old_files(previous.audio, kwargs.get("instance").audio)
    except sender.DoesNotExist as error:
        logging.debug(error)


@receiver(pre_save, sender=CardBackContent)
@receiver(pre_save, sender=CardTemplateBackContent)
def back_content_changed(sender, **kwargs):
    try:
        previous = sender.objects.get(id=kwargs.get("instance").id)
        delete_old_files(previous.audio, kwargs.get("instance").audio)
    except sender.DoesNotExist as error:
        logging.debug(error)
