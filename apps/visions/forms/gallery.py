# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from visions.models import Gallery


class GalleryForm(OrgModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' not in kwargs:
            return
        users_field = self.fields.get('users')
        if hasattr(users_field, 'queryset'):
            users_field.queryset = current_org.get_org_users()

    class Meta:
        model = Gallery
        exclude = (
            'id', 'date_created', 'created_by', 'org_id','music',
        )
        widgets = {
            'effects': forms.SelectMultiple(
                attrs={'class': 'select2', 'data-placeholder': _("Effect")}
            ),
        }
        labels = {
            'effects': _("Effect"),
        }

    def clean_asset_groups(self):
        effects = self.cleaned_data.get('effects')

        if not effects:
            raise forms.ValidationError(
                _("Asset or group at least one required"))

        return self.cleaned_data["effects"]
