from django.urls import path
from .views import (
    RejectionReasonAnalyticsView,
    SourceAnalyticsView,
    GroupsAnalyticsView,
)

urlpatterns = [
    path('rejection-reason-analytics/<int:year>', RejectionReasonAnalyticsView.as_view(), name='rejection_reason_analytics'),
    path('source-analytics/<int:year>', SourceAnalyticsView.as_view(), name='source_analytics'),
    path('groups-analytics/<int:year>', GroupsAnalyticsView.as_view(), name='groups_analytics'),
]
