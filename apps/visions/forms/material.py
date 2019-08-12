# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from visions.models import Material

class MaterialForm(OrgModelForm):

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            kwargs['initial'] = initial
        super().__init__(**kwargs)
        if 'initial' not in kwargs:
            return

    def save(self, commit=True):
        material = super().save(commit=commit)
        return material

    class Meta:
        model = Material
        fields = [
            'name', 'comment','video_name','video_path','start_time','end_time','is_active'
        ]


class FileForm(forms.Form):
    file = forms.FileField()

class MaterialBulkUpdateForm(OrgModelForm):
    materials = forms.ModelMultipleChoiceField(
        required=True,
        label=_('Select materials'),
        queryset=Material.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select materials')
            }
        )
    )

    class Meta:
        model = Material
        fields = ['materials','video_name','video_path','start_time','end_time','is_active']

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) is not None:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        materials = cleaned_data.pop('materials', '')
        materials = Material.objects.filter(id__in=[material.id for material in materials])
        materials.update(**cleaned_data)
        return materials