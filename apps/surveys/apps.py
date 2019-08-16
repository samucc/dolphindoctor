from __future__ import unicode_literals

from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = 'surveys'
    verbose_name = 'Surveys'

    def ready(self):
        from . import signals_handler
        return super().ready()
