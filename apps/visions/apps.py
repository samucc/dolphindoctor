from __future__ import unicode_literals

from django.apps import AppConfig


class VisionsConfig(AppConfig):
    name = 'visions'
    verbose_name = 'Visions'

    def ready(self):
        from . import signals_handler
        return super().ready()
