# -*- encoding: utf-8 -*-
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import RedirectImport
from subprocess import *

import os
import random


def get_directory_name(name):
    return '%s-%04x' % (name, random.randint(0, 0x10000))


def import_redirect(self, request, extra_context=None):
    path_to_logfile = ""
    if 'import' in request.session:
        path_to_logfile = os.path.join(request.session['import'], "info.log")
    logs = list()
    try:
        with open(path_to_logfile, 'r+') as logfile:
            for log in logfile.readlines():
                logs.append(log.rstrip())
    except IOError:
        pass
    logs.reverse()
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
            p = Popen(["python", "%s/manage.py" % settings.PROJECT_ROOT, "import_redirect", "-f%s"
                       %path, "-l%s" %path_to_logfile, "--change"])
            return HttpResponseRedirect('../')
        else:
            pass
    else:
        form = RedirectImport()
    disabled = False
    if 'import' in request.session:
        start = os.path.join(request.session['import'], "import_start")
        finish = os.path.join(request.session['import'], "import_finish")
        if os.path.exists(start) and not os.path.exists(finish):
            disabled = True
    context = {'form': form, 'logs': logs[:10], 'disabled': disabled}
    return render_to_response(
        'admin/import.html',
        context,
        context_instance=RequestContext(request)
    )



