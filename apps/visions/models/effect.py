# -*- coding: utf-8 -*-
import uuid

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelMixin

__all__ = ['Effect']


class Effect(OrgModelMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    method = models.CharField(max_length=128, blank=True, verbose_name=_('Method'))
    time_duration = models.CharField(max_length=128,default="", verbose_name=_('Time duration'))
    start_time = models.CharField(max_length=128, default="", verbose_name=_('Start time'))
    end_time = models.CharField(max_length=128, default="", verbose_name=_('End time'))

    comment = models.TextField(blank=True, verbose_name=_('Comment'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    date_created = models.DateTimeField(auto_now_add=True, null=True,
                                        verbose_name=_('Date created'))
    created_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = [('org_id', 'name'),]
        verbose_name = _("Effect")

    @classmethod
    def initial(cls):
        default_effect = cls.objects.filter(name='Default')
        if not default_effect:
            effect = cls(name='Default', created_by='System', comment='Default effect')
            effect.save()
        else:
            effect = default_effect[0]
        return effect

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from . import User

        seed()
        for i in range(count):
            effect = cls(name=forgery_py.name.full_name(),
                        comment=forgery_py.lorem_ipsum.sentence(),
                        created_by=choice(User.objects.all()).username)
            try:
                effect.save()
            except IntegrityError:
                print('Error continue')
                continue
