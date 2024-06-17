from .models import (
    Groups,
    Direction,
    GroupStatus,
    Times,
    Source,
    Application,
    RejectionReason,
)
from rest_framework import serializers
from users.serializers import (
    RegisterStudentSerializer, StudentInApplicationSerializer,
)
from users.models import Student


class RejectionReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectionReason
        fields = [
            'id',
            'title',
            'color',
        ]


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = [
            'id',
            'name',
            'duration',
            'color',
        ]


class TimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Times
        fields = [
            'id',
            'start_date',
            'end_date',
        ]


class GroupStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStatus
        fields = [
            'id',
            'name',
        ]


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = [
            'id',
            'name',
            'teacher',
            'direction',
            'audience',
            'number_of_students',
            'start_date',
            'end_date',
            'times',
            'timetable',
            'status',
        ]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = [
            'id',
            'name',
            'color',
        ]


class DirectionInApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Direction
        fields = ['id', 'name']


class SourceInApplication(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id', 'name']


class ApplicationListSerializer(serializers.ModelSerializer):
    student = StudentInApplicationSerializer(read_only=True)
    direction = DirectionInApplicationSerializer(read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')

    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            'direction',
            'status',
            'updated_at',
        ]


class GroupsInApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Groups
        fields = ['id', 'name']


class SourceInApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id', 'name', 'color']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    student = StudentInApplicationSerializer(required=False)
    direction = DirectionInApplicationSerializer(required=False)
    groups = GroupsInApplicationSerializer(required=False)
    source =SourceInApplication(required=False)


    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            'direction',
            'source',
            'groups',
            'status',
            'laptop'
        ]
        extra_kwargs = {
            'direction': {'required': False},
            'source': {'required': False},
            'status': {'required': False},
            'laptop': {'required': False},
        }

    def update(self, instance, validated_data):
        student_data = validated_data.pop('student', None)
        if student_data:
            student = instance.student
            student_serializer = StudentInApplicationSerializer(student, data=student_data)
            if student_serializer.is_valid():
                student_serializer.save()
            else:
                raise serializers.ValidationError({'error': student_serializer.errors})

        return super().update(instance, validated_data)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    student = StudentInApplicationSerializer(required=False)

    class Meta:
        model = Application
        fields = ['id', 'student', 'direction', 'source', 'status', 'groups', 'laptop', 'rejection_reason']

        extra_kwargs = {
            'direction': {'required': False},
            'source': {'required': False}
        }

    def update(self, instance, validated_data):
        student_data = validated_data.pop('student', None)
        if student_data:
            student = instance.student
            student_serializer = StudentInApplicationSerializer(student, data=student_data)
            if student_serializer.is_valid():
                if student.payment is None:
                    student_serializer.save()
                else:
                    try:
                        payment_int = int(student.payment)
                        new_payment_int = int(student_data.get('payment', payment_int))
                        student_serializer.validated_data['payment'] = str(payment_int + new_payment_int)
                        student_serializer.save()
                    except ValueError:
                        raise serializers.ValidationError({'error': 'Invalid payment value'})
            else:
                raise serializers.ValidationError({'error': student_serializer.errors})

        return super().update(instance, validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()
    # student = RegisterStudentSerializer()

    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            'groups',
            'direction',
            'laptop',
            'source',
            'status',
            'transaction',
            'rejection_reason',
            'reason_description',
            'created_at',
            'updated_at',
            'history',
        ]

    def get_history(self, obj):
        history_data = []
        current_version = None
        for history_instance in obj.history.all().order_by('history_date'):
            history_changes = {}
            previous_version = current_version
            current_version = history_instance
            if previous_version is not None:
                delta = current_version.diff_against(previous_version)

                for change in delta.changes:
                    history_changes[change.field] = {
                        'old': change.old,
                        'new': change.new,
                    }
            history_data.append({
                'id': history_instance.id,
                'action': history_instance.history_type,
                'timestamp': history_instance.history_date,
                'user': history_instance.history_user.email if history_instance.history_user else None,
                'changes': history_changes,
            })
        return history_data[::-1]


class ApplicationCreateSerializer(serializers.ModelSerializer):
    student = RegisterStudentSerializer()

    class Meta:
        model = Application
        fields = ['id', 'student', 'direction', 'source', 'status', 'groups', 'laptop']

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        student, _ = Student.objects.get_or_create(**student_data)
        application = Application.objects.create(student=student, **validated_data)
        return application
