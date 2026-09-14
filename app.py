"""Convenience entry point for running the Django dashboard locally."""
import os
import sys

from django.core.management import execute_from_command_line


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "policy_dashboard.settings")
    address = sys.argv[1:] or ["127.0.0.1:8000"]
    execute_from_command_line([sys.argv[0], "runserver", *address])
