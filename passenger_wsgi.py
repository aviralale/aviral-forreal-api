"""Phusion Passenger entrypoint for cPanel's "Setup Python App".

cPanel runs the app through Passenger, which imports `application` from this
file at the project root. We just point it at Django's WSGI app. cPanel manages
the virtualenv; environment variables come from the cPanel app config and/or
the project-root .env (loaded in config/settings.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from config.wsgi import application  # noqa: E402
