from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import CardFrontContent, CardTemplateFrontContent, CardTemplateBackContent, CardBackContent
from .tools import delete_file


@receiver(post_delete, sender=CardFrontContent)
@receiver(post_delete, sender=CardTemplateFrontContent)
def front_content_deleted(sender, **kwargs):
    if kwargs.get("instance").photo:
        delete_file(kwargs.get("instance").photo)
    if kwargs.get("instance").audio:
        delete_file(kwargs.get("instance").audio)


@receiver(post_delete, sender=CardBackContent)
@receiver(post_delete, sender=CardTemplateBackContent)
def front_content_deleted(sender, **kwargs):
    if kwargs.get("instance").audio:
        delete_file(kwargs.get("instance").audio)


@receiver(pre_save, sender=CardFrontContent)
@receiver(pre_save, sender=CardTemplateFrontContent)
def front_content_changed(sender, **kwargs):
    if sender.objects.filter(id=kwargs.get("instance").id).exists():
        old_photo = sender.objects.get(id=kwargs.get("instance").id).photo
        if old_photo and old_photo != kwargs.get("instance").photo:
            delete_file(old_photo)
        old_audio = sender.objects.get(id=kwargs.get("instance").id).audio
        if old_audio and old_audio != kwargs.get("instance").audio:
            delete_file(old_audio)


@receiver(pre_save, sender=CardBackContent)
@receiver(pre_save, sender=CardTemplateBackContent)
def back_content_changed(sender, **kwargs):
    if sender.objects.filter(id=kwargs.get("instance").id).exists():
        old_audio = sender.objects.get(id=kwargs.get("instance").id).audio
        if old_audio and old_audio != kwargs.get("instance").audio:
            delete_file(old_audio)
