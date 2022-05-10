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
    """
    File Validator class for audio files
    Allowed audio extensions and mime-types are: mp3 / wav / ogg

    For more info visit the link below
    https://madil.in/file-mime-type-validation-in-django/
    """
    messages = {
        "file_too_small": "File too small. Minimum file size is %(min_size)s",
        "file_too_large": "File too large. Maximum file size is %(max_size)s",
        "malicious_file": "Upload a valid audio. Allowed extensions are: '%(allowed_extensions)s'.",
        "not_supported": "File extension '%(extension)s' is not allowed. "
                         "Allowed extensions are: '%(allowed_extensions)s'."
    }
    code = 'invalid_extension'
    ext_cnt_mapping = {
        'mp3': ['audio/mpeg'],
        'wav': ['audio/wav', 'audio/x-wav'],
        'ogg': ['audio/ogg']
    }

    min_file_size = 4 * 1024  # 8KB
    max_file_size = 16 * 1024 * 1024  # 16MB
    code_size = 'invalid_size'

    def __init__(self, ):
        self.allowed_extensions = [allowed_extension.lower() for
                                   allowed_extension in self.ext_cnt_mapping.keys()]

    def __call__(self, data):
        if not self.min_file_size <= data.size:
            raise ValidationError(
                self.messages['file_too_small'],
                code=self.code_size,
                params={
                    'min_size': str(self.min_file_size / 1024) + " KB"
                }
            )
        if not self.max_file_size >= data.size:
            raise ValidationError(
                self.messages['file_too_large'],
                code=self.code_size,
                params={
                    'max_size': str(self.max_file_size / (1024 * 1024)) + " MB"
                }
            )

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
        if content_type not in self.ext_cnt_mapping[extension]:
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
