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
from visions.models import Music,Gallery
from visions.forms import MusicForm


class MusicListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/vision_music_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Music list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MusicCreateView(AdminUserRequiredMixin, CreateView):
    model = Music
    form_class = MusicForm
    template_name = 'visions/vision_music_create_update.html'
    success_url = reverse_lazy('visions:vision-music-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        gallerys_id = self.request.GET.get("gallerys")
        if gallerys_id:
            gallerys_id = gallerys_id.split(",")
            gallerys = Gallery.objects.filter(id__in=gallerys_id)
            form['gallerys'].initial = gallerys
        return form

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Create vision music'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MusicUpdateView(AdminUserRequiredMixin, UpdateView):
    model = Music
    form_class = MusicForm
    template_name = 'visions/vision_music_create_update.html'
    success_url = reverse_lazy("visions:vision-music-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision music')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MusicDetailView(AdminUserRequiredMixin, DetailView):
    model = Music
    form_class = MusicForm
    template_name = 'visions/vision_music_detail.html'
    success_url = reverse_lazy("visions:vision-music-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision music'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MusicDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Music
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-music-list')


class MusicAssetView(AdminUserRequiredMixin,
                               SingleObjectMixin,
                               ListView):
    template_name = 'visions/vision_music_gallery.html'
    context_object_name = 'music'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset = Music.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = list(self.object.get_all_gallerys())
        return queryset

    def get_context_data(self, **kwargs):
        gallerys_granted = self.get_queryset()
        context = {
            'app': _('visions'),
            'action': _('Music asset list'),
            'gallerys_remain': Gallery.objects.exclude(id__in=[a.id for a in gallerys_granted]),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)