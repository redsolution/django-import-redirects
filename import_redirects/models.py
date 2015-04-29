# -*- coding: utf-8 -*-
from django.contrib.redirects.models import Redirect
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib.sessions.models import Session

import os
import shutil


class ImportModel(Redirect):
    class Meta:
        verbose_name = _('Import redirects from csv-file')
        verbose_name_plural = _('Import redirects from csv-file')
        proxy = True
        app_label = "redirects"


@receiver(post_delete, sender=Session)
def close_session(sender, **kwargs):
    session = kwargs['instance']
    session_data = session.get_decoded()
    if 'import' in session_data:
        start = os.path.join(session_data['import'], "import_start")
        finish = os.path.join(session_data['import'], "import_finish")
        if os.path.exists(start) and os.path.exists(finish):
            try:
                shutil.rmtree(session_data['import'])
            except OSError:
                pass

