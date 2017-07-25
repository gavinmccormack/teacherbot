"""
WSGI config for grimpie project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
 
import os, sys

sys.path.append('/home/teachertest/public_html/cgi-bin/teacherbot')

# add the virtualenv site-packages path to the sys.path
sys.path.append(' /home/teachertest/virtualenv/public__html_cgi-bin/2.7/Lib/site-packages')

# pointing to the project settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teacherbot.settings")


from django.core.wsgi import get_wsgi_application



application = get_wsgi_application()

