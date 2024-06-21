import datetime

from django.db import models
from rest_framework.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from users.models import Student, Teacher, User


class Direction(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(null=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Times(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"


class GroupStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Groups(models.Model):
    AUDIENCE_CHOICES = ((1, "Маленькая"), (2, "Средняя"), (3, "Большая"))
    TIMETABLE_CHOICES = ((1, "Пн, Ср, Пт"), (2, "Вт, Чт, Сб"))
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        "users.teacher", on_delete=models.CASCADE, null=True, related_name="teacher"
    )
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, null=True)
    audience = models.PositiveSmallIntegerField(choices=AUDIENCE_CHOICES, default=1)
    number_of_students = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    times = models.ForeignKey(Times, on_delete=models.SET_NULL, null=True, blank=True)
    timetable = models.PositiveSmallIntegerField(choices=TIMETABLE_CHOICES, default=1)
    status = models.ForeignKey(
        GroupStatus, on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + datetime.timedelta(
            days=self.direction.duration * 30
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class RejectionReason(models.Model):
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class Application(models.Model):
    APPLICATION_CHOICES = (
        (1, "Ждет звонка"),
        (2, "Записался на пробный урок"),
        (3, "Посетил пробный урок"),
        (4, "Неуспешная сделка"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    groups = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    laptop = models.BooleanField(default=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(
        choices=APPLICATION_CHOICES, default=1, null=True, blank=True
    )
    transaction = models.BooleanField(default=False)
    rejection_reason = models.ForeignKey(
        RejectionReason, on_delete=models.SET_NULL, null=True
    )
    reason_description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(editable=True, auto_now_add=True)
    updated_at = models.DateTimeField(editable=True, auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.pk} of Student {self.student}"
