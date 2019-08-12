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
from visions.models import Classify
from visions.forms import ClassifyForm


class ClassifyListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'visions/vision_classify_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Classify list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ClassifyCreateView(AdminUserRequiredMixin, CreateView):
    model = Classify
    form_class = ClassifyForm
    template_name = 'visions/vision_classify_create_update.html'
    success_url = reverse_lazy('visions:vision-classify-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        nodes_id = self.request.GET.get("nodes")
        assets_id = self.request.GET.get("assets")

        if nodes_id:
            nodes_id = nodes_id.split(",")
            nodes = Node.objects.filter(id__in=nodes_id).exclude(id=Node.root().id)
            form['nodes'].initial = nodes
        if assets_id:
            assets_id = assets_id.split(",")
            assets = Asset.objects.filter(id__in=assets_id)
            form['assets'].initial = assets
        return form

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Create vision Classify'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ClassifyUpdateView(AdminUserRequiredMixin, UpdateView):
    model = Classify
    form_class = ClassifyForm
    template_name = 'visions/vision_classify_create_update.html'
    success_url = reverse_lazy("visions:vision-classify-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision Classify')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ClassifyDetailView(AdminUserRequiredMixin, DetailView):
    model = Classify
    form_class = ClassifyForm
    template_name = 'visions/vision_classify_detail.html'
    success_url = reverse_lazy("visions:vision-classify-list")

    def get_context_data(self, **kwargs):
        context = {
            'app': _('visions'),
            'action': _('Update vision Classify'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ClassifyDeleteView(AdminUserRequiredMixin, DeleteView):
    model = Classify
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('visions:vision-classify-list')


class ClassifyAssetView(AdminUserRequiredMixin,
                               SingleObjectMixin,
                               ListView):
    template_name = 'visions/vision_classify_asset.html'
    context_object_name = 'classify'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset = Classify.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = list(self.object.get_all_assets())
        return queryset

    def get_context_data(self, **kwargs):
        assets_granted = self.get_queryset()
        context = {
            'app': _('visions'),
            'action': _('Classify asset list'),
            'assets_remain': Asset.objects.exclude(id__in=[a.id for a in assets_granted]),
            'nodes_remain': Node.objects.exclude(granted_by_visions_classify=self.object),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)