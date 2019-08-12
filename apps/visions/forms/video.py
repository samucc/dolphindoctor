# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelForm
from orgs.utils import current_org
from visions.models import Video

class VideoForm(OrgModelForm):

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            kwargs['initial'] = initial
        super().__init__(**kwargs)
        if 'initial' not in kwargs:
            return

    def save(self, commit=True):
        video = super().save(commit=commit)
        return video

    class Meta:
        model = Video
        fields = [
            'name', 'comment','category','show','show_time','is_active'
        ]


class FileForm(forms.Form):
    file = forms.FileField()

class VideoBulkUpdateForm(OrgModelForm):
    videos = forms.ModelMultipleChoiceField(
        required=True,
        label=_('Select videos'),
        queryset=Video.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select videos')
            }
        )
    )

    class Meta:
        model = Video
        fields = ['videos','category','show','show_time','is_active']

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) is not None:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        videos = cleaned_data.pop('videos', '')
        videos = Video.objects.filter(id__in=[video.id for video in videos])
        videos.update(**cleaned_data)
        return videos