import logging
import os
import uuid

logger = logging.getLogger(__name__)


def get_card_content_path(instance, filename):
    logger.info("Content file '%s' was uploaded for card '%s'" % (filename, instance.card.name))
    return os.path.join("deck_%s" % instance.card.deck.id, "card_%s" % instance.card.id, str(uuid.uuid1()))
