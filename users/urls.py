from django.urls import path
from rest_framework import routers

from .views import (
    AdminProfileRetrieveUpdateView,
    ChangePasswordView,
    ConfirmCodeView,
    ForgotPasswordView,
    LoginView,
    RefreshTokenView,
    RegisterOfficeManagerView,
    RegisterStudentView,
    RegisterTeacherView,
    StudentViewSet,
    TeacherViewSet,
    UserAndTeacherListView,
)

users_router = routers.DefaultRouter()
users_router.register(r"students", StudentViewSet, basename="list-of-students")
users_router.register(r"teachers", TeacherViewSet, basename="list-of-teachers")

urlpatterns = [
    path(
        "register/office_mannager/",
        RegisterOfficeManagerView.as_view(),
        name="register_office_manager",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh_token"),
    path(
        "profile/me/",
        AdminProfileRetrieveUpdateView.as_view(),
        name="retrieve_update_profile",
    ),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("confirm-code/", ConfirmCodeView.as_view(), name="confirm-code"),
    path("register/teacher/", RegisterTeacherView.as_view(), name="register_teacher"),
    path("register/student/", RegisterStudentView.as_view(), name="register_student"),
    path("all_staff/", UserAndTeacherListView.as_view(), name="all_staff"),
]
