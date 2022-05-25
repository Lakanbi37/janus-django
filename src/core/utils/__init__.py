import os
import random
import string

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def file_path():
    return os.path.join(settings.LOCAL_FILE_DIR, 'images')


def transaction_id(_range=24):
    return ''.join(random.choice(string.ascii_letters) for x in range(_range))


def image_upload_to(instance, filename):
    return "images/{0}/{1}/logo/{2}_{3}".format(instance.__class__.__name__, str(instance), str(instance), filename)


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
try:
    AUTH_USER_APP_LABEL, AUTH_USER_MODEL_NAME = AUTH_USER_MODEL.rsplit('.', 1)
except ValueError:
    raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form"
                               " 'app_label.model_name'")
