from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from applications.urls import applications_router
from patches import routers
from users.urls import users_router

router = routers.DefaultRouter()
router.extend(applications_router)
router.extend(users_router)

schema_view = get_schema_view(
    openapi.Info(
        title="CRM Neolabs API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(
        r"^crm_neolabs/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^crm_neolabs/swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^crm_neolabs/redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("crm_neolabs/admin/", admin.site.urls),
    path("crm_neolabs/users/", include("users.urls")),
    path("crm_neolabs/", include(router.urls)),
    path("crm_neolabs/application/", include("applications.urls")),
    path("crm_neolabs/analytics/", include("analytics.urls")),
    path("crm_neolabs/notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
