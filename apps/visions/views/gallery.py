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
from visions.models import Gallery,Effect
from visions.forms import GalleryForm


class GalleryListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/vision_gallery_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Gallery list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GalleryCreateView(AdminUserRequiredMixin, CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'visions/vision_gallery_create_update.html'
    success_url = reverse_lazy('visions:vision-gallery-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        effects_id = self.request.GET.get("effects")

        if effects_id:
            effects_id = effects_id.split(",")
            effects = Effect.objects.filter(id__in=effects_id)
            form['effects'].initial = effects
        return form

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Create vision gallery'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GalleryUpdateView(AdminUserRequiredMixin, UpdateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'visions/vision_gallery_create_update.html'
    success_url = reverse_lazy("visions:vision-gallery-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision gallery')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GalleryDetailView(AdminUserRequiredMixin, DetailView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'visions/vision_gallery_detail.html'
    success_url = reverse_lazy("visions:vision-gallery-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision gallery'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class GalleryDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Gallery
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-gallery-list')


class GalleryAssetView(AdminUserRequiredMixin,
                               SingleObjectMixin,
                               ListView):
    template_name = 'visions/vision_gallery_effect.html'
    context_object_name = 'gallery'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset = Gallery.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = list(self.object.get_all_effects())
        return queryset

    def get_context_data(self, **kwargs):
        effects_granted = self.get_queryset()
        context = {
            'app': _('visions'),
            'action': _('Gallery asset list'),
            'effects_remain': Effect.objects.exclude(id__in=[a.id for a in effects_granted]),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)