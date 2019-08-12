# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from visions.models import Music


class MusicForm(OrgModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' not in kwargs:
            return
        users_field = self.fields.get('users')
        if hasattr(users_field, 'queryset'):
            users_field.queryset = current_org.get_org_users()

    class Meta:
        model = Music
        exclude = (
            'id', 'date_created', 'created_by', 'org_id'
        )
        widgets = {
            'gallerys': forms.SelectMultiple(
                attrs={'class': 'select2', 'data-placeholder': _("Gallery")}
            ),
        }
        labels = {
            'gallerys': _("Gallery"),
        }

    def clean_asset_groups(self):
        gallerys = self.cleaned_data.get('gallerys')

        if not gallerys:
            raise forms.ValidationError(
                _("Asset or group at least one required"))

        return self.cleaned_data["gallerys"]
