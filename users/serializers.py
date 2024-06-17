from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, fields
from .models import User, Teacher, Student
from .services import UserService


class RegisterOfficeManagerSerializer(serializers.ModelSerializer):
    work_days = fields.MultipleChoiceField(choices=User.DAYS_OF_WEEK)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'work_days', 'start_work_time', 'end_work_time']

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password']


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"error": "Password fields didn't match."})

        return attrs


class ForgotPasswordByPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, min_length=13)

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class ResetPasswordByPhoneSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, min_length=6)


class RegisterTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'patent_number', 'patent_term']

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class RegisterStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'email',
            'is_blacklist',
            'status',
        ]


class StudentInApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'payment'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'payment': {'required': False}
        }

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class TeacherSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    work_days = fields.MultipleChoiceField(choices=User.DAYS_OF_WEEK)

    class Meta:
        model = Teacher
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'email',
            'patent_number',
            'patent_term',
            'role',
            'work_days',
            'start_work_time',
            'end_work_time'
        ]

    def get_role(self, teacher: Teacher):
        return 'teacher'

    def validate_phone(self, value):
        return UserService.validate_phone(value)



class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'phone', 'email', 'role', ]

    def get_role(self, user: User):
        if user.is_superuser:
            return "superadmin"
        return "office_manager"

    def get_full_name(self, user: User):
        return f"{user.first_name} {user.last_name}"

    def validate_phone(self, value):
        return UserService.validate_phone(value)


class ProfileDetailSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone', 'email', 'role', ]

    def get_role(self, user: User):
        if user.is_superuser:
            return "superadmin"
        return "office_manager"

    def get_full_name(self, user: User):
        return f"{user.first_name} {user.last_name}"


class OfficeManagerListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'role', 'phone']

    def get_role(self, user: User):
        return "office_manager"

    def get_full_name(self, user: User):
        return f"{user.first_name} {user.last_name}"





class TeacherListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()


    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'full_name', 'role', 'direction', 'phone']

    def get_role(self, user: User):
        return "teacher"

    def get_full_name(self, user: User):
        return f"{user.first_name} {user.last_name}"

    def get_direction(self, teacher: Teacher):
        direction = None
        group = teacher.groups.first()  # assuming a teacher can be assigned to multiple groups, but here we are taking only the first one
        if group:
            direction = group.direction.name
        return direction