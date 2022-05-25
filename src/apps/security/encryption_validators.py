import functools
from django.utils.functional import lazy
from django.conf import settings
from django.contrib.auth.password_validation import (
    get_password_validators,
    validate_password,
    password_changed,
    password_validators_help_texts,
    _password_validators_help_text_html
)


@functools.lru_cache(maxsize=None)
def get_default_encryption_validators():
    return get_password_validators(settings.ENCRYPTION_KEY_VALIDATORS)


def validate_encryption_key(key, file=None, encryption_validators=None):
    if encryption_validators is None:
        encryption_validators = get_default_encryption_validators()
    return validate_password(key, file, encryption_validators)


def encryption_key_changed(key, file=None, validators=None):
    if validators is None:
        validators = get_default_encryption_validators()
    return password_changed(key, file, validators)


def encryption_validator_help_text(encryption_validator=None):
    if encryption_validator is None:
        encryption_validator = get_default_encryption_validators()
    return password_validators_help_texts(encryption_validator)


def _key_validators_html_help_texts(validators):
    return _password_validators_help_text_html(validators)


encryption_key_validation_help_text = lazy(_key_validators_html_help_texts, str)