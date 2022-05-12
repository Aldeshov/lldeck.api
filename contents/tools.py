import logging
import os
import random
import string
import uuid

logger = logging.getLogger(__name__)


def get_card_content_path(instance, filename):
    logger.info("Content file '%s' was uploaded for card '%s'" % (filename, instance.card.name))
    return os.path.join(
        "contents",
        "%s-%s" % (instance.card.deck.__class__.__name__.lower(), instance.card.deck.id),
        "card-%s" % instance.card.id, str(uuid.uuid1()) + os.path.splitext(filename)[1]
    )


def get_deck_preview_path(instance, filename):
    logger.info("Preview file '%s' was uploaded for deck '%s'" % (filename, instance.name))
    return os.path.join(
        "previews",
        instance.__class__.__name__.lower(),
        str(uuid.uuid1()) + os.path.splitext(filename)[1]
    )


def random_string(length=32):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def delete_file(file):
    if os.path.isfile(file.path):
        os.remove(file.path)


def delete_empty_dirs(file_path, recursion=True):
    parent = os.path.abspath(os.path.join(file_path, os.pardir))
    if os.path.isdir(parent) and not os.listdir(parent):
        os.rmdir(parent)

    if recursion:
        delete_empty_dirs(parent, False)


def delete_old_files(old_file, new_file):
    if old_file and old_file != new_file:
        delete_file(old_file)

    if not new_file and old_file:
        delete_empty_dirs(old_file.path)
