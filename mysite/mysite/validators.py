import re

from difflib import SequenceMatcher
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.translation import ugettext as _, ungettext


class NumberValidator(object):
    def validate(self,password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("bolekkkkk"),
                code="password_no_number"
            )

class NumericPasswordValidator:
    """
    Sprawdź, czy hasło jest alfanumeryczne
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("To hasło jest całkowicie numeryczne"),
                code='password_entirely_numeric'
            )
    def get_help_text(self):
        return _("Twoje hasło nie może być całkowicie numeryczne")

class UserAttributeSimilarityValidator:
    """
    Sprawdż, czy hasło jest wystarczajaco różne od attrybutów użytkownika
    """
    DEFAULT_USER_ATTRIBUTES = ('username', 'email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]

            for value_parts in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_parts.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("Hasło jest zbyt podobne do %(verbose_name)s."),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )
    def get_help_text(self):
        return _("Twoje hasło nie może być zbyt podobne do Twoich innych danych.")

class MinimumLengthValidator(object):
    """
    Sprawdź, czy hasło ma minimalną długość.
    """
    def __init__(self, min_length = 8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ungettext(
                    "To hasło jest zbyt krótkie. Musi składać się co najmniej z %(min_length)d znak",
                    "To hasło jest zbyt krótkie. Musi składać się co najmniej z %(min_length)d znaków",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ungettext(
                    "To hasło jest zbyt krótkie. Musi składać się co najmniej z %(min_length)d znak",
                    "To hasło jest zbyt krótkie. Musi składać się co najmniej z %(min_length)d znaków",
                    self.min_length
                ) % {'min_length': self.min_length}
