# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView,DeleteView, SingleObjectMixin
from django.views.generic.detail import DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from common.utils import get_logger
from common.const import create_success_msg, update_success_msg
from common.permissions import AdminUserRequiredMixin
from orgs.utils import current_org
from ..models import Video
from ..forms import video
from common.const import (
    create_success_msg, update_success_msg, KEY_CACHE_RESOURCES_ID
)

__all__ = ['VideoListView', 'VideoCreateView', 'VideoDetailView',
           'VideoUpdateView','VideoDeleteView','VideoBulkUpdateView']
logger = get_logger(__name__)


class VideoListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/video_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Video list')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Video
    form_class = video.VideoForm
    template_name = 'visions/video_create_update.html'
    success_url = reverse_lazy('visions:vision-video-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Create video'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Video
    form_class = video.VideoForm
    template_name = 'visions/video_create_update.html'
    success_url = reverse_lazy('visions:vision-video-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Update video'),

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoDetailView(AdminUserRequiredMixin, DetailView):
    model = Video
    context_object_name = 'video'
    template_name = 'visions/video_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Video detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class VideoDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Video
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-video-list')

class VideoBulkUpdateView(AdminUserRequiredMixin, TemplateView):
    model = Video
    form_class = video.VideoBulkUpdateForm
    template_name = 'visions/video_bulk_update.html'
    success_url = reverse_lazy('visions:vision-video-list')
    success_message = _("Bulk update video success")
    form = None
    id_list = None

    def get(self, request, *args, **kwargs):
        spm = request.GET.get('spm', '')
        videos_id = cache.get(KEY_CACHE_RESOURCES_ID.format(spm))
        if kwargs.get('form'):
            self.form = kwargs['form']
        elif videos_id:
            self.form = self.form_class(initial={'videos': videos_id})
        else:
            self.form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            return self.get(request, form=form, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'app': 'Visions',
            'action': _('Bulk update video'),
            'form': self.form,
            'videos_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
