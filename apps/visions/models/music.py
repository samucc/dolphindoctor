import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from common.utils import date_expired_default, set_or_append_attr_bulk

from orgs.mixins import OrgModelMixin, OrgManager


class MusicQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def valid(self):
        # return self.active().filter(date_start__lt=timezone.now())\
        #     .filter(date_expired__gt=timezone.now())
        return self.active()


class MusicManager(OrgManager):
    def valid(self):
        return self.get_queryset().valid()


class Music(OrgModelMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    address = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('Address'))
    max_power = models.CharField(max_length=54, null=True, blank=True,
                             verbose_name=_('Max power')) #最大功率 KW
    manager = models.CharField(max_length=54, null=True, blank=True,
                             verbose_name=_('Manager')) #管理员
    space = models.CharField(max_length=54, null=True, blank=True,
                             verbose_name=_('Space')) #平方英尺
    longitude = models.FloatField(null=True, blank=True, verbose_name=_('Longitude'))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_('Latitude'))
    gallerys = models.ManyToManyField('visions.Gallery', related_name='granted_by_visions_music', blank=True, verbose_name=_("Gallery"))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_by = models.CharField(max_length=128, blank=True, verbose_name=_('Created by'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    comment = models.TextField(verbose_name=_('Comment'), blank=True)

    objects = MusicManager.from_queryset(MusicQuerySet)()

    class Meta:
        unique_together = [('org_id', 'name')]
        verbose_name = _("Music")

    def __str__(self):
        return self.name

    @property
    def id_str(self):
        return str(self.id)

    @property
    def is_valid(self):
        # if self.date_expired > timezone.now() > self.date_start and self.is_active:
        if self.is_active:
            return True
        return False

    def get_all_gallerys(self):
        gallerys = set(self.gallerys.all())
        return gallerys

    def to_dict(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = str(getattr(self, field.name))
        return d
