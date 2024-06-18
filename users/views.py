import random
import string

from django.core.mail import send_mail
from django.db.models import Q
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from drf_multiple_model.views import (
    FlatMultipleModelAPIView,
    ObjectMultipleModelAPIView,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    exceptions,
    filters,
    generics,
    status,
    viewsets,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAcceptable,
    NotFound,
    ValidationError,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from applications.pagination import CustomPagination
from cms import settings

from .models import (
    OTP,
    Student,
    Teacher,
    User,
)
from .permissions import IsSuperUser
from .serializers import (
    ChangePasswordSerializer,
    ConfirmationCodeSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    OfficeManagerListSerializer,
    OfficeManagerSerializer,
    ProfileDetailSerializer,
    ProfileSerializer,
    RegisterOfficeManagerSerializer,
    RegisterStudentSerializer,
    RegisterTeacherSerializer,
    StudentSerializer,
    TeacherListSerializer,
    TeacherSerializer,
)
from .utils import Util


class RegisterOfficeManagerView(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser)
    serializer_class = RegisterOfficeManagerSerializer

    @swagger_auto_schema(request_body=RegisterOfficeManagerSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterOfficeManagerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email").lower()
        phone = request.data.get("phone")
        work_days = request.data.get("work_days")
        start_work_time = request.data.get("start_work_time")
        end_work_time = request.data.get("end_work_time")
        password = "".join(random.choice(string.digits) for _ in range(6))
        User.objects.create_user(
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            work_days=work_days,
            start_work_time=start_work_time,
            end_work_time=end_work_time,
            is_staff=True,
        )
        body = f"Здравствуйте, {last_name} {first_name}!\nВаш пароль: {password}"

        data = {
            "email_body": body,
            "to_email": email,
            "email_subject": "Ваш пароль!",
        }

        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterTeacherView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsSuperUser)
    serializer_class = RegisterTeacherSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterTeacherSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        Teacher.objects.create_teacher(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterStudentView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsSuperUser)
    serializer_class = RegisterStudentSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterStudentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        Student.objects.create_student(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        self.perform_authentication(request)
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed(detail={"error": "User not found!"})
        if not user.check_password(password):
            raise AuthenticationFailed(detail={"error": "Incorrect password!"})

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user_id": user.id,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

    def perform_authentication(self, request):
        """
        Removes any existing authentication from the request.
        """
        request.user = None
        request.auth = None


class RefreshTokenView(TokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"access": str(serializer.validated_data["access"])},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("password"))
            self.object.save()
            return Response(
                data={"message": ("Password changed successfully!")},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"error": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE
        )


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Этот эндпоинт предоставляет возможность сбросить пароль пользователя по email.",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            otp_code = OTP.generate_otp()
            OTP.objects.create(user=user, otp=otp_code)
            # Send the OTP to the user's email
            subject = "Forgot Password OTP"
            message = f"Your OTP is: {otp_code}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            return Response(
                {"message": "OTP sent to your email."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmCodeView(generics.GenericAPIView):
    serializer_class = ConfirmationCodeSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Этот эндпоинт позволяет "
        "подтвердить код подтверждения, "
        "который был отправлен на адрес "
        "электронной почты пользователя "
        "после успешной регистрации. После "
        "подтверждения кода, система выдает новый "
        "токен доступа (Access Token) и обновления "
        "(Refresh Token) для пользователя.",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get("code")
        try:
            confirmation_code = OTP.objects.get(otp=code)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid or already confirmed code."}, status=400)

        user = confirmation_code.user
        confirmation_code.delete()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Code confirmed successfully.",
                "user_id": str(user.id),
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "patent_number"]
    ordering_fields = ["first_name", "last_name", "email", "patent_number"]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name", "email", "status"]


class OfficeManagerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = OfficeManagerListSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name", "email"]


class AdminProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ProfileDetailSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class UserAndTeacherListView(FlatMultipleModelAPIView):
    # pagination_class = CustomPagination
    querylist = [
        {
            "queryset": User.objects.all(),
            "serializer_class": OfficeManagerListSerializer,
        },
        {
            "queryset": Teacher.objects.all(),
            "serializer_class": TeacherListSerializer,
        },
    ]

    def get_queryset(self):
        search = self.request.query_params.get("search", None)
        if search:
            # Update each queryset in the querylist with a filtered queryset
            for query in self.querylist:
                model = query["queryset"].model
                if model == User:
                    query["queryset"] = query["queryset"].filter(
                        Q(first_name__icontains=search) | Q(last_name__icontains=search)
                    )
                elif model == Teacher:
                    query["queryset"] = query["queryset"].filter(
                        Q(first_name__icontains=search) | Q(last_name__icontains=search)
                    )
        return super().get_queryset()

    def get_serializer_class(self):
        for query in self.querylist:
            if self.get_queryset() == query["queryset"]:
                return query["serializer_class"]
        return None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search query",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
