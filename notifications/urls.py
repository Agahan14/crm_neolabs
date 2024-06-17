from django.urls import path
from .views import PushNotificationView

urlpatterns = [
    path('send/', PushNotificationView.as_view(), name='send_notification')
]
