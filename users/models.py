import random
import string

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from .managers import UserManager

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    DAYS_OF_WEEK = (
        ("1", "Пн"),
        ("2", "Вт"),
        ("3", "Ср"),
        ("4", "Чт"),
        ("5", "Пт"),
        ("6", "Сб"),
        ("7", "Вс"),
    )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True, null=True, blank=True)
    work_days = MultiSelectField(
        max_choices=7,
        choices=DAYS_OF_WEEK,
        null=True,
        blank=True,
        validators=[MaxValueValidator(7)],
    )
    start_work_time = models.DateTimeField(null=True, blank=True)
    end_work_time = models.DateTimeField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"


class Teacher(User):
    patent_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    patent_term = models.DateField(null=True, blank=True)


class Student(User):
    STUDYING = "Обучается"
    FINISHED = "Закончил"
    INTERRUPTED = "Прервал обучение"
    STATUS_CHOICES = ((1, STUDYING), (2, FINISHED), (3, INTERRUPTED))
    is_blacklist = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, null=True, blank=True
    )
    payment = models.CharField(max_length=200, null=True, blank=True)


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        digits = string.digits
        return "".join(random.choice(digits) for i in range(4))

    @property
    def is_expired(self):
        time_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return self.created_at < time_threshold
