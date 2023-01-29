import os
import sys

import yatube.settings as s


def main():
    print(
        'Type ',
        'no_debug=1 python manage.py runserver ',
        'to run in no debug mode.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')
    if os.environ.get('no_debug'):
        print("Debug disabled.")
        s.DEBUG = False
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
