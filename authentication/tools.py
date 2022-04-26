import logging
import os
import uuid

logger = logging.getLogger(__name__)


def get_user_avatar_path(instance, filename):
    logger.info("Avatar (image file) '%s' was uploaded by the user '%s'" % (filename, instance.name))
    return os.path.join("avatars", str(uuid.uuid1()))


def delete_file(file):
    if os.path.isfile(file.path):
        os.remove(file.path)
