import os
import sys
import teacherbot.wsgi

sys.path.insert(0, os.path.dirname(__file__))

application = teacherbot.wsgi.application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teacherbot.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()