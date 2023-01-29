from django.forms import ValidationError


def not_empty_text_validator(value):
    if value == '':
        raise ValidationError(
            'А кто поле будет заполнять, Пушкин?',
            params={'value': value},
        )
