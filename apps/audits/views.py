import csv
import json
import uuid
import codecs


from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.utils.translation import ugettext as _
from django.db.models import Q

from audits.utils import get_excel_response, write_content_to_excel
from common.mixins import DatetimeSearchMixin
from common.permissions import PermissionsMixin, IsOrgAdmin, IsAuditor, IsValidUser

from orgs.utils import current_org
from .models import FTPLog, OperateLog, PasswordChangeLog, UserLoginLog


def get_resource_type_list():
    from users.models import User, UserGroup
    from assets.models import (
        Asset, Node, AdminUser, SystemUser, Gateway
    )
    from orgs.models import Organization
    # from perms.models import AssetPermission

    models = [
        User, UserGroup, Asset, Node, AdminUser, SystemUser,
        Gateway, Organization
    ]
    return [model._meta.verbose_name for model in models]



class OperateLogListView(PermissionsMixin, DatetimeSearchMixin, ListView):
    model = OperateLog
    template_name = 'audits/operate_log_list.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    user = action = resource_type = ''
    date_from = date_to = None
    actions_dict = dict(OperateLog.ACTION_CHOICES)
    permission_classes = [IsOrgAdmin | IsAuditor]

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.user = self.request.GET.get('user')
        self.action = self.request.GET.get('action')
        self.resource_type = self.request.GET.get('resource_type')

        filter_kwargs = dict()
        filter_kwargs['datetime__gt'] = self.date_from
        filter_kwargs['datetime__lt'] = self.date_to
        if self.user:
            filter_kwargs['user'] = self.user
        if self.action:
            filter_kwargs['action'] = self.action
        if self.resource_type:
            filter_kwargs['resource_type'] = self.resource_type
        if filter_kwargs:
            self.queryset = self.queryset.filter(**filter_kwargs).order_by('-datetime')
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'user_list': current_org.get_org_users(),
            'actions': self.actions_dict,
            'resource_type_list': get_resource_type_list(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            'resource_type': self.resource_type,
            "app": _("Audits"),
            "action": _("Operate log"),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class PasswordChangeLogList(PermissionsMixin, DatetimeSearchMixin, ListView):
    model = PasswordChangeLog
    template_name = 'audits/password_change_log_list.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    user = ''
    date_from = date_to = None
    permission_classes = [IsOrgAdmin | IsAuditor]

    def get_queryset(self):
        users = current_org.get_org_users()
        self.queryset = super().get_queryset().filter(
            user__in=[user.__str__() for user in users]
        )
        self.user = self.request.GET.get('user')

        filter_kwargs = dict()
        filter_kwargs['datetime__gt'] = self.date_from
        filter_kwargs['datetime__lt'] = self.date_to
        if self.user:
            filter_kwargs['user'] = self.user
        if filter_kwargs:
            self.queryset = self.queryset.filter(**filter_kwargs).order_by('-datetime')
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'user_list': current_org.get_org_users(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            "app": _("Audits"),
            "action": _("Password change log"),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class LoginLogListView(PermissionsMixin, DatetimeSearchMixin, ListView):
    template_name = 'audits/login_log_list.html'
    model = UserLoginLog
    paginate_by = settings.DISPLAY_PER_PAGE
    user = keyword = ""
    date_to = date_from = None
    permission_classes = [IsOrgAdmin | IsAuditor]

    @staticmethod
    def get_org_users():
        users = current_org.get_org_users().values_list('username', flat=True)
        return users

    def get_queryset(self):
        if current_org.is_default():
            queryset = super().get_queryset()
        else:
            users = self.get_org_users()
            queryset = super().get_queryset().filter(username__in=users)

        self.user = self.request.GET.get('user', '')
        self.keyword = self.request.GET.get("keyword", '')

        queryset = queryset.filter(
            datetime__gt=self.date_from, datetime__lt=self.date_to
        )
        if self.user:
            queryset = queryset.filter(username=self.user)
        if self.keyword:
            queryset = queryset.filter(
                Q(ip__contains=self.keyword) |
                Q(city__contains=self.keyword) |
                Q(username__contains=self.keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Audits'),
            'action': _('Login log'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            'keyword': self.keyword,
            'user_list': self.get_org_users(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class LoginLogExportView(PermissionsMixin, View):
    permission_classes = [IsValidUser]

    def get(self, request):
        fields = [
            field for field in UserLoginLog._meta.fields
        ]
        filename = 'login-logs-{}.csv'.format(
            timezone.localtime(timezone.now()).strftime('%Y-%m-%d_%H-%M-%S')
        )
        excel_response = get_excel_response(filename)
        header = [field.verbose_name for field in fields]
        login_logs = cache.get(request.GET.get('spm', ''), [])

        response = write_content_to_excel(excel_response, login_logs=login_logs,
                                          header=header, fields=fields)
        return response

    def post(self, request):
        try:
            date_form = json.loads(request.body).get('date_form', [])
            date_to = json.loads(request.body).get('date_to', [])
            user = json.loads(request.body).get('user', [])
            keyword = json.loads(request.body).get('keyword', [])

            login_logs = UserLoginLog.get_login_logs(
                date_form=date_form, date_to=date_to, user=user, keyword=keyword)
        except ValueError:
            return HttpResponse('Json object not valid', status=400)
        spm = uuid.uuid4().hex
        cache.set(spm, login_logs, 300)
        url = reverse('audits:login-log-export') + '?spm=%s' % spm
        return JsonResponse({'redirect': url})