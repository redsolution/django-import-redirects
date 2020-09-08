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
import os
import random


def get_directory_name(name):
    return '%s-%04x' % (name, random.randint(0, 0x10000))


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
            path = default_storage.save(os.path.join(request.session['import'], 'redirects.csv'),
                                        ContentFile(data.read()))
            if path_to_logfile == "":
                path_to_logfile = default_storage.save(os.path.join(request.session['import'], "info.log"),
                                                       ContentFile(""))
            p = Popen(["python", "%s/manage.py" % settings.BASE_DIR, "import_redirect", "-f%s"
                       %path, "-l%s" %path_to_logfile, "--change"])
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



