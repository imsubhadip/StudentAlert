#!/usr/bin/env python
"""Django's command-line utility (runserver, migrate, etc.)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_system.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print("Django is not installed. Activate your virtual environment and run:")
        print("    pip install -r requirements.txt")
        sys.exit(1)
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
