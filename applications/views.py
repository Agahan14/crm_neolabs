from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, generics, views

from users.models import Student, Teacher, User
from users.serializers import (
    StudentSerializer,
    TeacherSerializer,
)
from users.services import UserService

from .models import (
    Application,
    Direction,
    Groups,
    GroupStatus,
    RejectionReason,
    Source,
    Times,
)
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    ApplicationSerializer,
    ApplicationUpdateSerializer,
    DirectionSerializer,
    GroupsSerializer,
    GroupStatusSerializer,
    RejectionReasonSerializer,
    SourceSerializer,
    TimesSerializer,
)
from .services import ApplicationService


class RejectionReasonViewSet(ModelViewSet):
    queryset = RejectionReason.objects.all()
    serializer_class = RejectionReasonSerializer


class GroupsViewSet(ModelViewSet):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class DirectionViewSet(ModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer


class GroupStatusViewSet(ModelViewSet):
    queryset = GroupStatus.objects.all()
    serializer_class = GroupStatusSerializer


class TimesViewSet(ModelViewSet):
    queryset = Times.objects.all()
    serializer_class = TimesSerializer


class SourceViewSet(ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class ApplicationListView(generics.ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationListSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_fields = ["status"]
    search_fields = ["student__first_name", "student__last_name", "groups__name"]


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": serializer.data}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class ApplicationRetrieveUpdateDeleteView(generics.GenericAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        application = ApplicationService.get(id=kwargs["pk"])
        serializer = ApplicationDetailSerializer(application)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        application = ApplicationService.get(id=kwargs["pk"])
        serializer = self.get_serializer(application, data=request.data)

        if not serializer.is_valid():
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        application = ApplicationService.get(id=kwargs["pk"])
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserArchieveUpdateRetrieveView(views.APIView):
    def post(self, request, *args, **kwargs):
        user = UserService.get(id=kwargs["pk"])

        if not user.is_archive:
            user.is_archive = True
            user.save()
        else:
            raise ValidationError(detail={"error": "This user is already archived!"})
        return Response(
            data={"message": ("User successfully archived!")}, status=status.HTTP_200_OK
        )


class UserUnarchieveUpdateRetrieveView(views.APIView):
    def post(self, request, *args, **kwargs):
        user = UserService.get(id=kwargs["pk"])
        if user.is_archive:
            user.is_archive = False
            user.save()
        else:
            raise ValidationError(detail={"error": "This user is already unarchived!"})
        return Response(
            data={"message": ("User successfully unarchived!")},
            status=status.HTTP_200_OK,
        )


class GlobalSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get("q", "")
        # Используем Q-объекты для поиска по нескольким полям и моделям
        groups = Groups.objects.filter(
            Q(name__icontains=search_query)
            | Q(teacher__first_name__icontains=search_query)
            | Q(direction__name__icontains=search_query)
        )
        applications = Application.objects.filter(
            Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(groups__name__icontains=search_query)
            | Q(direction__name__icontains=search_query)
        )
        teachers = Teacher.objects.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(patent_number__icontains=search_query)
        )
        students = Student.objects.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        )

        # Сериализуем результаты поиска и отправляем обратно
        data = {
            "groups": GroupsSerializer(groups, many=True).data,
            "applications": ApplicationSerializer(applications, many=True).data,
            "teachers": TeacherSerializer(teachers, many=True).data,
            "students": StudentSerializer(students, many=True).data,
        }
        return Response(data)


class AddToStudentView(views.APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "application_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the application to add to student",
                )
            },
        ),
        operation_description="Add application to student and change student status to STUDYING",
    )
    def post(self, request, *args, **kwargs):
        application = ApplicationService.get(id=kwargs["pk"])
        try:
            student = application.student
        except:
            raise NotFound(detail={"error": ("Student not found!")})

        if not application.transaction:
            application.transaction = True
            application.status = None
            application.save()
            student.status = 1
            student.save()
        return Response(
            data={"message": ("Student successfully added!")}, status=status.HTTP_200_OK
        )
