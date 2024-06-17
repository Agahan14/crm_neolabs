from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

User = get_user_model()


class UserService:
    model = User

    @classmethod
    def get(cls, **filters):
        try:
            return cls.model.objects.get(**filters)
        except cls.model.DoesNotExist:
            raise NotFound(detail={'error': ('User not found!')})

    @classmethod
    def validate_phone(cls, value):
        if not value[1:].isnumeric():
            raise serializers.ValidationError({'error':'Phone must be numeric symbols'})
        if value[:4] != '+996':
            raise serializers.ValidationError({'error':'Phone number should start with +996 '})
        elif len(value) != 13:
            raise serializers.ValidationError({'error':'Phone number must be 13 characters long'})
        return value