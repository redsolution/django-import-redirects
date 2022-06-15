# -*- encoding: utf-8 -*-
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.context import RequestContext
from .forms import RedirectImport
from subprocess import *
from django.urls import reverse

from django.core.cache import cache
from django.utils.six.moves import input
from django.db import transaction
from django.db.utils import DatabaseError
from django.contrib.redirects.models import Redirect

import os
import random
import csv
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
LOCK_EXPIRE = 60 * 10
acquire_lock = lambda: cache.add("import_redirects", 'true', LOCK_EXPIRE)
release_lock = lambda: cache.delete("import_redirects")


def get_directory_name(name):
    return '%s-%04x' % (name, random.randint(0, 0x10000))


def import_csv(file, logfile):
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if acquire_lock():
        try:
            if not file:
                raise Exception('You must provide path to csv-file. Use -f option.')
            path_to_file = os.path.normpath(file)
            if not os.path.exists(path_to_file):
                raise Exception('File not found')
            if os.path.isdir(path_to_file):
                raise Exception('%s is a directory' % path_to_file)
            with open(path_to_file, 'r') as csvfile:
                try:
                    dialect = csv.Sniffer().sniff(csvfile.readline(), delimiters=';,')
                    csvfile.seek(0)
                    data = csv.DictReader(csvfile, fieldnames=['old_path', 'new_path'], dialect=dialect)
                except csv.Error:
                    mess = 'Incorrect file format'
                    logger.error(mess)
                    raise Exception(mess)
                with transaction.atomic():
                    try:
                        for i, row in enumerate(data):
                            old_path = row['old_path']
                            new_path = row['new_path']
                            if not old_path.startswith("/"):
                                mess = 'LINE: %s. Invalid url: %s' % (i + 1, old_path)
                                logger.error(mess)
                                raise Exception(mess)
                            if not new_path.startswith("/"):
                                mess = 'LINE: %s. Invalid url: %s' % (i + 1, new_path)
                                logger.error(mess)
                                raise Exception(mess)
                            redirect, created = Redirect.objects.get_or_create(site_id=settings.SITE_ID,
                                                                               old_path=old_path)
                            if created:
                                redirect.new_path = new_path
                                redirect.save()
                            else:
                                if redirect.new_path != new_path:
                                    change = ""
                                    if not options.get('change'):
                                        self.stdout.write('\nRedirect %s exist. Change to %s ---> %s ?:\n'
                                                          % (redirect.__unicode__(), old_path, new_path))
                                        change = input('"y" for Yes or "n" for No (leave blank for "n"): ')
                                    if change == "y" or options.get('change'):
                                        redirect.new_path = new_path
                                        redirect.save()
                    except DatabaseError:
                        mess = 'Error in transaction. Please repeat import'
                        logger.error(mess)
                        raise
            logger.info('Import completed successfully')
        finally:
            release_lock()
    else:
        logger.error('Redirects is already being imported. Please repeat later')


def import_redirect(self, request, extra_context=None):
    path_to_logfile = ""
    if 'import' in request.session:
        path_to_logfile = os.path.join(request.session['import'], "info.log")

    if request.method == 'POST':
        form = RedirectImport(request.POST,  request.FILES)
        if form.is_valid():
            data = request.FILES['file']
            if not 'import' in request.session:
                path_dir = os.path.join(settings.MEDIA_ROOT, "import_redirect")
                import_dir = ""
                while True:
                    import_dir = get_directory_name(path_dir)
                    try:
                        os.mkdir(import_dir)
                        break
                    except OSError:
                        pass
                request.session['import'] = import_dir
            path = os.path.join(request.session['import'], 'redirects.csv')
            default_storage.save(path, ContentFile(data.read()))
            if path_to_logfile == "":
                path_to_logfile = os.path.join(request.session['import'], "info.log")
                default_storage.save(path_to_logfile, ContentFile(""))
            p = import_csv(path, path_to_logfile)
    else:
        form = RedirectImport()
    disabled = False
    if cache.get("import_redirects"):
        messages.warning(request, _('Redirects is already being imported. Please repeat later'))
        disabled = True

    logs = list()
    try:
        with open(path_to_logfile, 'r+') as logfile:
            for log in logfile.readlines():
                logs.append(log.rstrip())
    except IOError:
        pass
    logs.reverse()

    context = {'form': form, 'logs': logs[:10], 'disabled': disabled}
    return render(request, 'admin/import.html', context)



