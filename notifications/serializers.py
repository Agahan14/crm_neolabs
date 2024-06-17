from rest_framework import serializers
from .models import Notifcation

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notifcation
        fields = ['id', 'title', 'body']