# -*- coding: utf-8 -*-
from django.contrib.redirects.models import Redirect
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib.sessions.models import Session

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
        if not cache.get("import_redirects"):
            try:
                shutil.rmtree(session_data['import'])
            except (shutil.Error, OSError):
                pass

