import string

from django.core.exceptions import ValidationError

allowed_tag_characters = set(string.ascii_lowercase + string.digits + '-')


def validate_tag_name(value: str):
    if len(value) < 3:
        raise ValidationError('Must have at least 3 characters')

    if not set(value.lower()) <= allowed_tag_characters:
        raise ValidationError('Includes NOT ALLOWED characters. List of allowed: %s' % ['a-z', 'A-Z', '0-9', '-'])
