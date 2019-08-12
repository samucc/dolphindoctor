# -*- coding: utf-8 -*-
import uuid

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelMixin

__all__ = ['Material']


class Material(OrgModelMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    video_name = models.CharField(max_length=128,default="", verbose_name=_('Video name'))
    video_path = models.CharField(max_length=128,blank=True,  verbose_name=_('Video path'))
    start_time = models.CharField(max_length=128,default="",  verbose_name=_('Start time'))
    end_time = models.CharField(max_length=128,default="",  verbose_name=_('End time'))

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
        verbose_name = _("Material")

    @classmethod
    def initial(cls):
        default_material = cls.objects.filter(name='Default')
        if not default_material:
            material = cls(name='Default', created_by='System', comment='Default material')
            material.save()
        else:
            material = default_material[0]
        return material

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from . import User

        seed()
        for i in range(count):
            material = cls(name=forgery_py.name.full_name(),
                        comment=forgery_py.lorem_ipsum.sentence(),
                        created_by=choice(User.objects.all()).username)
            try:
                material.save()
            except IntegrityError:
                print('Error continue')
                continue


