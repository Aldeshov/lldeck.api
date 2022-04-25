import logging
import os
import uuid


def get_user_avatar_path(instance, filename):
    logging.info(f"Avatar (image file) '{filename}' was uploaded by the user '{instance.name}'")
    return os.path.join(b"avatars", uuid.uuid1().bytes)
