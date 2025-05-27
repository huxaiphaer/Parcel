import logging
import os

from celery import Celery
from celery.signals import after_setup_logger
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Parcels.settings")

app = Celery("Parcels")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    logger.info("Celery logger set up")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setting up periodic tasks")
