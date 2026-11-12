"""WSGI file - used by PythonAnywhere (and other servers) to run the project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_system.settings")

application = get_wsgi_application()
