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
from ..models import Effect
from ..forms import effect
from common.const import (
    create_success_msg, update_success_msg, KEY_CACHE_RESOURCES_ID
)

__all__ = ['EffectListView', 'EffectCreateView', 'EffectDetailView',
           'EffectUpdateView','EffectDeleteView','EffectBulkUpdateView']
logger = get_logger(__name__)


class EffectListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/effect_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Effect list')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class EffectCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Effect
    form_class = effect.EffectForm
    template_name = 'visions/effect_create_update.html'
    success_url = reverse_lazy('visions:vision-effect-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Create effect'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class EffectUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Effect
    form_class = effect.EffectForm
    template_name = 'visions/effect_create_update.html'
    success_url = reverse_lazy('visions:vision-effect-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Update effect'),

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class EffectDetailView(AdminUserRequiredMixin, DetailView):
    model = Effect
    context_object_name = 'effect'
    template_name = 'visions/effect_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Visions'),
            'action': _('Effect detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class EffectDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Effect
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-effect-list')

class EffectBulkUpdateView(AdminUserRequiredMixin, TemplateView):
    model = Effect
    form_class = effect.EffectBulkUpdateForm
    template_name = 'visions/effect_bulk_update.html'
    success_url = reverse_lazy('visions:vision-effect-list')
    success_message = _("Bulk update effect success")
    form = None
    id_list = None

    def get(self, request, *args, **kwargs):
        spm = request.GET.get('spm', '')
        effects_id = cache.get(KEY_CACHE_RESOURCES_ID.format(spm))
        if kwargs.get('form'):
            self.form = kwargs['form']
        elif effects_id:
            self.form = self.form_class(initial={'effects': effects_id})
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
            'action': _('Bulk update effect'),
            'form': self.form,
            'effects_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
