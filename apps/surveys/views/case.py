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
from ..models import Case
from ..forms import case
from common.const import (
    create_success_msg, update_success_msg, KEY_CACHE_RESOURCES_ID
)

__all__ = ['CaseListView', 'CaseCreateView', 'CaseDetailView',
           'CaseUpdateView','CaseDeleteView','CaseBulkUpdateView']
logger = get_logger(__name__)


class CaseListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'surveys/case_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Surveys'),
            'action': _('Case list')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CaseCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Case
    form_class = case.CaseForm
    template_name = 'surveys/case_create_update.html'
    success_url = reverse_lazy('surveys:survey-case-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Surveys'),
            'action': _('Create case'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CaseUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Case
    form_class = case.CaseForm
    template_name = 'surveys/case_create_update.html'
    success_url = reverse_lazy('surveys:survey-case-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Surveys'),
            'action': _('Update case'),

        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CaseDetailView(AdminUserRequiredMixin, DetailView):
    model = Case
    context_object_name = 'case'
    template_name = 'surveys/case_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Surveys'),
            'action': _('Case detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class CaseDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Case
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('surveys:survey-case-list')

class CaseBulkUpdateView(AdminUserRequiredMixin, TemplateView):
    model = Case
    form_class = case.CaseBulkUpdateForm
    template_name = 'surveys/case_bulk_update.html'
    success_url = reverse_lazy('surveys:survey-case-list')
    success_message = _("Bulk update case success")
    form = None
    id_list = None

    def get(self, request, *args, **kwargs):
        spm = request.GET.get('spm', '')
        cases_id = cache.get(KEY_CACHE_RESOURCES_ID.format(spm))
        if kwargs.get('form'):
            self.form = kwargs['form']
        elif cases_id:
            self.form = self.form_class(initial={'cases': cases_id})
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
            'app': 'Surveys',
            'action': _('Bulk update case'),
            'form': self.form,
            'cases_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
