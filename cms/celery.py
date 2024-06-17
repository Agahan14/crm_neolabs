from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cms.settings")

app = Celery("cms")

# finds all rows that have the name celery in settings
app.config_from_object('django.conf:settings', namespace="CELERY")

# so that it automatically finds the task
app.autodiscover_tasks()

# celery beat tasks
app.conf.beat_schedule = {
    'print-hello-world-5-minute': {
        'task': 'applications.tasks.hello_world',
        'schedule': crontab(minute='*/180')
    },
}

