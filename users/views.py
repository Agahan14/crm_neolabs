import random
import string

from django.db.models import Value, CharField
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    status,
    exceptions,
    generics,
    viewsets,
    filters,
)
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAcceptable,
    ValidationError,
    NotFound,
)
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from twilio.rest import Client

from .permissions import IsSuperUser
from .serializers import (
    RegisterOfficeManagerSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    ForgotPasswordByPhoneSerializer,
    ResetPasswordByPhoneSerializer,
    RegisterTeacherSerializer,
    RegisterStudentSerializer,
    StudentSerializer,
    TeacherSerializer,
    ProfileSerializer,
    ProfileDetailSerializer,
    OfficeManagerListSerializer,
    TeacherListSerializer

)
from .utils import Util
from .models import (
    User,
    PasswordResetByPhone,
    Teacher,
    Student,
)


class RegisterOfficeManagerView(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser)
    serializer_class = RegisterOfficeManagerSerializer

    @swagger_auto_schema(request_body=RegisterOfficeManagerSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterOfficeManagerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={
                'error': serializer.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email').lower()
        phone = request.data.get('phone')
        work_days = request.data.get('work_days')
        start_work_time = request.data.get('start_work_time')
        end_work_time = request.data.get('end_work_time')
        password = ''.join(random.choice(string.digits) for _ in range(6))
        User.objects.create_user(
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            work_days=work_days,
            start_work_time=start_work_time,
            end_work_time=end_work_time,
            is_staff=True
        )
        body = f'Здравствуйте, {last_name} {first_name}!\nВаш пароль: {password}'

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
            return Response(data={
                'error': serializer.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        Teacher.objects.create_teacher(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterStudentView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsSuperUser)
    serializer_class = RegisterStudentSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterStudentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={
                'error': serializer.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

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
            raise AuthenticationFailed(detail={'error': 'User not found!'})
        if not user.check_password(password):
            raise AuthenticationFailed(detail={'error': 'Incorrect password!'})

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'user_id': user.id,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK
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
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "access": str(serializer.validated_data['access'])
        }, status=status.HTTP_200_OK)


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
                data={'message': ('Password changed successfully!')}, status=status.HTTP_200_OK
            )
        return Response(data={'error': serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ForgotPasswordByPhoneAPIView(APIView):

    @swagger_auto_schema(request_body=ForgotPasswordByPhoneSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordByPhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={
                'error': serializer.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        phone = serializer.validated_data.get('phone')
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise NotAcceptable(detail={'error': 'Please enter a valid phone.'})
        token = ''.join(random.choice(string.digits) for _ in range(6))

        PasswordResetByPhone.objects.create(phone=phone, token=token)

        account_sid = "AC5d8b15f5528be5064555d9c42a419bed"
        auth_token = "70b9658004c15ca11705c851e755a8a1"
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body='Your verification PIN is: ' + token,
            from_="+19066805628",
            to=phone,
        )

        return Response({
            'message': 'Please check your phone!'
        }, status=status.HTTP_200_OK)


class ResetPasswordByPhoneAPIView(APIView):

    @swagger_auto_schema(request_body=ResetPasswordByPhoneSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordByPhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={
                'error': serializer.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        token = serializer.validated_data.get('token')

        passwordResetByPhone = PasswordResetByPhone.objects.filter(token=token).first()

        if passwordResetByPhone is None:
            raise ValidationError(detail={'error': 'Token not valid!'})

        if token != passwordResetByPhone.token:
            raise exceptions.APIException(detail={'error': 'Code is incorrect!'})

        user = User.objects.filter(phone=passwordResetByPhone.phone).first()

        if not user:
            raise NotFound(detail={'error': ('User not found!')})

        passwordResetByPhone.delete()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'user_id': str(user.id),
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK
        )


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'patent_number']
    ordering_fields = ['first_name', 'last_name', 'email', 'patent_number']
    

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'email', 'status']


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
            return Response(data={'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class UserAndTeacherListView(FlatMultipleModelAPIView):

    querylist = [
        {'queryset': User.objects.all(), 'serializer_class': OfficeManagerListSerializer},
        {'queryset': Teacher.objects.all(), 'serializer_class': TeacherListSerializer},
    ]

    def get_serializer_class(self):
        for query in self.querylist:
            if self.get_queryset() == query['queryset']:
                return query['serializer_class']
        return None
