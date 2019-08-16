# -*- coding: utf-8 -*-
import uuid

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelMixin

__all__ = ['Case']


class Case(OrgModelMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    disease_code = models.CharField(max_length=128, blank=True, verbose_name=_('Disease code'))
    case_number = models.CharField(max_length=128, blank=True, verbose_name=_('Case Number'))
    name = models.CharField(max_length=128,blank=True, verbose_name=_('Name'))

    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    date_created = models.DateTimeField(auto_now_add=True, null=True,
                                        verbose_name=_('Date created'))
    created_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = [('org_id', 'name'),]
        verbose_name = _("Case")

    @classmethod
    def initial(cls):
        default_case = cls.objects.filter(name='Default')
        if not default_case:
            case = cls(name='Default', created_by='System')
            case.save()
        else:
            case = default_case[0]
        return case

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from . import User

        seed()
        for i in range(count):
            case = cls(disease_code=forgery_py.name.full_name(),
                        created_by=choice(User.objects.all()).username)
            try:
                case.save()
            except IntegrityError:
                print('Error continue')
                continue
