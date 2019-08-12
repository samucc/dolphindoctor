# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from visions.models import Effect

class EffectForm(OrgModelForm):

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            kwargs['initial'] = initial
        super().__init__(**kwargs)
        if 'initial' not in kwargs:
            return

    def save(self, commit=True):
        effect = super().save(commit=commit)
        return effect

    class Meta:
        model = Effect
        fields = [
            'name', 'comment','method','time_duration','start_time','end_time','is_active'
        ]


class FileForm(forms.Form):
    file = forms.FileField()

class EffectBulkUpdateForm(OrgModelForm):
    effects = forms.ModelMultipleChoiceField(
        required=True,
        label=_('Select effects'),
        queryset=Effect.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select effects')
            }
        )
    )

    class Meta:
        model = Effect
        fields = ['effects','method','time_duration','start_time','end_time','is_active']

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) is not None:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        effects = cleaned_data.pop('effects', '')
        effects = Effect.objects.filter(id__in=[effect.id for effect in effects])
        effects.update(**cleaned_data)
        return effects