""" This module contain the celery configurations """

from celery import Celery
from os import environ
import logging
from logging.handlers import RotatingFileHandler



def make_celery(app=None):
    """Create and configure the Celery instance."""

    celery_instance = Celery(
        app.import_name if app else __name__,
        backend=environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )

    celery_instance.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        include=['website.celery.tasks'],  # Explicitly include the tasks module
    )

    #environ["IS_CELERY_WORKER"] = "True"

    # Logging setup for Celery and tasks
    handler = RotatingFileHandler('celery_tasks.log', maxBytes=10240, backupCount=1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)

    # Configure the logger for Celery task logs
    task_logger = logging.getLogger('celery_task_logger')
    task_logger.addHandler(handler)
    task_logger.setLevel(logging.INFO)

    if app:
        # Define ContextTask to bind Flask's app context
        class ContextTask(celery_instance.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super().__call__(*args, **kwargs)
        app.config["IS_CELERY_WORKER"] = True

        celery_instance.Task = ContextTask

    return celery_instance
