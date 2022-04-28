import logging
import os
import uuid

logger = logging.getLogger(__name__)


def get_card_content_path(instance, filename):
    logger.info("Content file '%s' was uploaded for card '%s'" % (filename, instance.card.name))
    return os.path.join(
        "%s-%s" % (instance.card.deck.__class__.__name__.lower(), instance.card.deck.id),
        "card-%s" % instance.card.id, str(uuid.uuid1()) + os.path.splitext(filename)[1]
    )


def delete_file(file):
    if os.path.isfile(file.path):
        os.remove(file.path)
