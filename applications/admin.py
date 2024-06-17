from django.contrib import admin
from .models import (
    Direction, Times, GroupStatus, Groups, Source, Application, RejectionReason
)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'groups',
        'direction',
        'laptop',
        'source',
        'status',
        'transaction',
        'created_at',
        'updated_at',)


admin.site.register(Application, ApplicationAdmin)
admin.site.register([Direction, Times, Groups, GroupStatus, Source, RejectionReason])
