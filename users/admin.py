from django.contrib import admin
from .models import User, PasswordResetByPhone, Student, Teacher
# Register your models here.

admin.site.register([User, PasswordResetByPhone, Student, Teacher])