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
from ..models import Material
from ..forms import material
from common.const import (
    create_success_msg, update_success_msg, KEY_CACHE_RESOURCES_ID
)

__all__ = ['MaterialListView', 'MaterialCreateView', 'MaterialDetailView',
           'MaterialUpdateView','MaterialDeleteView','MaterialBulkUpdateView']
logger = get_logger(__name__)


class MaterialListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/material_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Material list')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MaterialCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Material
    form_class = material.MaterialForm
    template_name = 'visions/material_create_update.html'
    success_url = reverse_lazy('visions:vision-material-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Create material'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MaterialUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Material
    form_class = material.MaterialForm
    template_name = 'visions/material_create_update.html'
    success_url = reverse_lazy('visions:vision-material-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Update material'),

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MaterialDetailView(AdminUserRequiredMixin, DetailView):
    model = Material
    context_object_name = 'material'
    template_name = 'visions/material_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Material detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class MaterialDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Material
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-material-list')

class MaterialBulkUpdateView(AdminUserRequiredMixin, TemplateView):
    model = Material
    form_class = material.MaterialBulkUpdateForm
    template_name = 'visions/material_bulk_update.html'
    success_url = reverse_lazy('visions:vision-material-list')
    success_message = _("Bulk update material success")
    form = None
    id_list = None

    def get(self, request, *args, **kwargs):
        spm = request.GET.get('spm', '')
        materials_id = cache.get(KEY_CACHE_RESOURCES_ID.format(spm))
        if kwargs.get('form'):
            self.form = kwargs['form']
        elif materials_id:
            self.form = self.form_class(initial={'materials': materials_id})
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
            'action': _('Bulk update material'),
            'form': self.form,
            'materials_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
