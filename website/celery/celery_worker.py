""" This is module that handle the celery logic """
#from eventlet import monkey_patch
#monkey_patch()

from website.celery.celery_config import make_celery
from os import environ

# Initialize the Flask app and Celery instance
#flask_app = create_app()

#celery = make_celery(flask_app)

# Run the worker (only if this script is run directly)
#if __name__ == '__main__':
#    with flask_app.app_context():
#        celery.start()


celery = None  # Global variable for the Celery instance


def get_celery():
    """Initialize and return the Celery instance."""
    global celery
    if celery is None:
        #print('prev celery environ["IS_CELERY_WORKER"]: ', environ["IS_CELERY_WORKER"])
        #environ["IS_CELERY_WORKER"] = "True"
        #print('now celery environ["IS_CELERY_WORKER"]: ', environ["IS_CELERY_WORKER"])

        if "IS_CELERY_WORKER" not in environ:
            environ["IS_CELERY_WORKER"] = "True"

        from website import create_app
        flask_app = create_app()
        #flask_app.config["IS_CELERY_WORKER"] = True
        celery = make_celery(flask_app)
    return celery


# Run the worker (only if this script is run directly)
if __name__ == '__main__':
    celery = get_celery()
    with celery.app.app_context():
        celery.start()
