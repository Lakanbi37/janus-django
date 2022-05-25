from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils.translation import gettext_lazy as _
from . import encryption_validators


class Encryption(models.Model):
    key = models.CharField(_("Encryption Key"), max_length=128, null=True, blank=True)
    is_encrypted = models.BooleanField(default=False)
    _key = None

    class Meta:
        abstract = True
        verbose_name = "Encryption"
        verbose_name_plural = "Encryption"

    def save(self, *args, **kwargs):
        if self.key is not None:
            self.is_encrypted = True
        if self._key is not None:
            encryption_validators.encryption_key_changed(self._key, self)
            self._key = None
        super().save(*args, **kwargs)

    @property
    def model_is_encrypted(self):
        return bool(self.key is not None)

    def set_encryption_key(self, raw_key):
        self.key = make_password(raw_key)
        self._key = raw_key

    def check_encryption_key(self, raw_key):
        def setter(raw_password):
            self.set_encryption_key(raw_key)
            # Password hash upgrades shouldn't be considered password changes.
            self._key = None
            self.save(update_fields=["key"])
        return check_password(raw_key, self.key, setter)
