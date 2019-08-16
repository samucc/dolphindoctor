# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from surveys.models import Case

class CaseForm(OrgModelForm):

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            kwargs['initial'] = initial
        super().__init__(**kwargs)
        if 'initial' not in kwargs:
            return

    def save(self, commit=True):
        case = super().save(commit=commit)
        return case

    class Meta:
        model = Case
        fields = [
            'name','disease_code','case_number','is_active'
        ]


class FileForm(forms.Form):
    file = forms.FileField()

class CaseBulkUpdateForm(OrgModelForm):
    cases = forms.ModelMultipleChoiceField(
        required=True,
        label=_('Select cases'),
        queryset=Case.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select cases')
            }
        )
    )

    class Meta:
        model = Case
        fields = ['name','cases','disease_code','case_number','is_active']

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) is not None:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        cases = cleaned_data.pop('cases', '')
        cases = Case.objects.filter(id__in=[case.id for case in cases])
        cases.update(**cleaned_data)
        return cases