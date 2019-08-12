# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.views.generic.edit import DeleteView, SingleObjectMixin
from django.urls import reverse_lazy
from django.conf import settings

from common.permissions import AdminUserRequiredMixin
from orgs.utils import current_org
from visions.hands import Node, Asset
from visions.models import VideoCombine,Video
from visions.forms import VideoCombineForm


class VideoCombineListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/vision_video_combine_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Video combine list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoCombineCreateView(AdminUserRequiredMixin, CreateView):
    model = VideoCombine
    form_class = VideoCombineForm
    template_name = 'visions/vision_video_combine_create_update.html'
    success_url = reverse_lazy('visions:vision-video-combine-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        videos_id = self.request.GET.get("videos")

        if videos_id:
            videos_id = videos_id.split(",")
            videos = Video.objects.filter(id__in=videos_id)
            form['videos'].initial = videos
        return form

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Create vision video combine'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoCombineUpdateView(AdminUserRequiredMixin, UpdateView):
    model = VideoCombine
    form_class = VideoCombineForm
    template_name = 'visions/vision_video_combine_create_update.html'
    success_url = reverse_lazy("visions:vision-video-combine-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision video combine')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoCombineDetailView(AdminUserRequiredMixin, DetailView):
    model = VideoCombine
    form_class = VideoCombineForm
    template_name = 'visions/vision_video_combine_detail.html'
    success_url = reverse_lazy("visions:vision-video-combine-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision video combine'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VideoCombineDeleteView(AdminUserRequiredMixin, DeleteView):
    model = VideoCombine
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-video-combine-list')


class VideoCombineAssetView(AdminUserRequiredMixin,
                               SingleObjectMixin,
                               ListView):
    template_name = 'visions/vision_video_combine_video.html'
    context_object_name = 'video_combine'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset = VideoCombine.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = list(self.object.get_all_videos())
        return queryset

    def get_context_data(self, **kwargs):
        videos_granted = self.get_queryset()
        context = {
            'app': _('visions'),
            'action': _('Video combine asset list'),
            'videos_remain': Video.objects.exclude(id__in=[a.id for a in videos_granted]),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)