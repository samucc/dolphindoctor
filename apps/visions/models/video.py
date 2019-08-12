# -*- coding: utf-8 -*-
import uuid

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from orgs.mixins import OrgModelMixin

__all__ = ['Video']


class Video(OrgModelMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    category = models.CharField(max_length=128, blank=True, verbose_name=_('Category'))#韩综
    show = models.CharField(max_length=128, blank=True, verbose_name=_('show'))#RM
    show_time = models.CharField(max_length=128, blank=True, verbose_name=_('Show Time'))#2017
    name = models.CharField(max_length=128, verbose_name=_('Name'))#E357.170702.mkv
    #path=show/show_time/name

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
        verbose_name = _("Video")

    @classmethod
    def initial(cls):
        default_video = cls.objects.filter(name='Default')
        if not default_video:
            video = cls(name='Default', created_by='System', comment='Default video')
            video.save()
        else:
            video = default_video[0]
        return video

    @classmethod
    def generate_fake(cls, count=100):
        from random import seed, choice
        import forgery_py
        from . import User

        seed()
        for i in range(count):
            video = cls(name=forgery_py.name.full_name(),
                        comment=forgery_py.lorem_ipsum.sentence(),
                        created_by=choice(User.objects.all()).username)
            try:
                video.save()
            except IntegrityError:
                print('Error continue')
                continue
