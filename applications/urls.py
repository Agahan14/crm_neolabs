from django.urls import path
from rest_framework import routers
from .views import (
    DirectionViewSet,
    TimesViewSet,
    GroupStatusViewSet,
    GroupsViewSet,
    SourceViewSet,
    ApplicationListView,
    ApplicationCreateView,
    ApplicationRetrieveUpdateDeleteView,
    RejectionReasonViewSet,
    UserArchieveUpdateRetrieveView,
    UserUnarchieveUpdateRetrieveView,
    GlobalSearchView,
    AddToStudentView,
)

applications_router = routers.DefaultRouter()
applications_router.register(r'directions', DirectionViewSet, basename='directions')
applications_router.register(r'times', TimesViewSet, basename='times')
applications_router.register(r'group-status', GroupStatusViewSet, basename='group-status')
applications_router.register(r'groups', GroupsViewSet, basename='groups')
applications_router.register(r'source', SourceViewSet, basename='source')
applications_router.register(r'rejection-reason', RejectionReasonViewSet, basename='rejection-reason')

urlpatterns = [
    path('user/archive/<int:pk>', UserArchieveUpdateRetrieveView.as_view(), name='user_arhive'),
    path('user/unarchive/<int:pk>', UserUnarchieveUpdateRetrieveView.as_view(), name='user_arhive'),
    path('global-search/', GlobalSearchView.as_view(), name='global_search'),
    path('student/add/<int:pk>', AddToStudentView.as_view(), name='add_student'),
    path('', ApplicationListView.as_view(), name='applications_list'),
    path('create/', ApplicationCreateView.as_view(), name='application_create'),
    path('<int:pk>/', ApplicationRetrieveUpdateDeleteView.as_view(), name='application_detail_update_deletee'),
]
