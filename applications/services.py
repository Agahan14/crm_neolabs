from .models import Application
from rest_framework.exceptions import NotFound

class ApplicationService:
    model = Application

    @classmethod
    def get(cls, **filters):
        try:
            return cls.model.objects.get(**filters)
        except cls.model.DoesNotExist:
            raise NotFound(detail={'error': ('Application not found!')})
