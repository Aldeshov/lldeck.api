import string
from pathlib import Path

import magic
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

allowed_tag_characters = set(string.ascii_lowercase + string.digits + '-')


def validate_tag_name(value: str):
    if len(value) < 3:
        raise ValidationError('Must have at least 3 characters')

    if not set(value.lower()) <= allowed_tag_characters:
        raise ValidationError('Includes NOT ALLOWED characters. List of allowed: %s' % ['a-z', 'A-Z', '0-9', '-'])


@deconstructible
class AudioFileMimeValidator:
    messages = {
        "malicious_file": "Upload a valid audio. Allowed extensions are: '%(allowed_extensions)s'.",
        "not_supported": "File extension '%(extension)s' is not allowed. "
                         "Allowed extensions are: '%(allowed_extensions)s'."
    }
    code = 'invalid_extension'
    ext_cnt_mapping = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'x-wav': 'audio/x-wav',
        'ogg': 'audio/ogg'
    }

    def __init__(self, ):
        self.allowed_extensions = [allowed_extension.lower() for
                                   allowed_extension in self.ext_cnt_mapping.keys()]

    def __call__(self, data):
        extension = Path(data.name).suffix[1:].lower()
        content_type = magic.from_buffer(data.read(1024), mime=True)
        if extension not in self.allowed_extensions:
            raise ValidationError(
                self.messages['not_supported'],
                code=self.code,
                params={
                    'extension': extension,
                    'allowed_extensions': ', '.join(self.allowed_extensions)
                }
            )
        if content_type != self.ext_cnt_mapping[extension]:
            raise ValidationError(
                self.messages['malicious_file'],
                code=self.code,
                params={
                    'allowed_extensions': ', '.join(self.allowed_extensions)
                }
            )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.allowed_extensions == other.allowed_extensions and
                self.message == other.message and
                self.code == other.code
        )
