import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netflixBack.settings")

app = Celery("netflixBack")

# Использование настроек из settings.py с префиксом CELERY_ для конфигурации Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")