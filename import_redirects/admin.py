# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import ImportModel
from .views import import_redirect


class ImportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/import.html'
    changelist_view = import_redirect

    def has_add_permission(self, request):
        return False


admin.site.register(ImportModel, ImportAdmin)
