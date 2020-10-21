# Django import redirects

Django application for import redirects from csv file

## Requirements
- Django 2.2.*
- Python 3.5

## Installation and basic usage
1. Install package:

    ``pip install git+git://github.com/shoker174/django-import-redirects``

2. Configure your settings file:

    ```python
    MIDDLEWARE += ['django.contrib.redirects.middleware.RedirectFallbackMiddleware']

    INSTALLED_APPS += [
        'django.contrib.redirects',
        'import_redirects',
    ]
    ```
3. Create ``import.csv`` file with two columns, for example:
	```
    /old-path/;/new-path/
    /old-path/sub-path/;/new-path/sub-path/
    ```
4. Import file in admin app interface