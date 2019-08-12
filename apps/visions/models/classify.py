import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from common.utils import date_expired_default, set_or_append_attr_bulk

from orgs.mixins import OrgModelMixin, OrgManager
from .material import Material

class ClassifyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def valid(self):
        # return self.active().filter(date_start__lt=timezone.now())\
        #     .filter(date_expired__gt=timezone.now())
        return self.active()


class ClassifyManager(OrgManager):
    def valid(self):
        return self.get_queryset().valid()


class Classify(OrgModelMixin):
    DEVICE_TYPE = (
        ("switch", _("Switch")),  # ("交换机", "交换机"),
        ("x86", _("X86")),  # ("X86", "X86"),
        ("vm", _("VM")),  # 虚拟机
        ("storage", _("Storage")),  # ("储存", "储存"),
        ("small_machine", _("Small Machine")),  # ("小机", "小机"),
        ("firewall", _("Firewall")),  # ("防火墙", "防火墙"),
        ("load_balancer", _("Load Balancer")),  # ("负载均衡器", "负载均衡器"),
        ("optical_switch", _("Optical Switch")),
        ("power_linux", _("Power Linux")),  # ("POWER Linux", "POWER Linux"),
        ("appliance", _("Appliance")),#器械，装置
        ("chassis", _("Chassis")),#底座支架
        ("patch_panel", _("Patch Panel")),# 配线板
        ("physical_vision", _("Physical Visions")),# 物理基础设施
        ("other", _("Other")),  # ("其他", "其他"),
    )
    SNMP_VERSION = (
        ("1", _("1")),
        ("2c", _("2c")),
        ("3", _("3")),
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    model = models.CharField(max_length=54, null=True, blank=True,verbose_name=_('Model'))
    height = models.CharField(max_length=54, null=True, blank=True,verbose_name=_('Height'))# 高度
    weight = models.CharField(max_length=54, null=True, blank=True,verbose_name=_('Weight'))# 重量
    rated_power = models.CharField(max_length=54, null=True, blank=True,verbose_name=_('Rated power'))# 额定功率
    device_type = models.CharField(choices=DEVICE_TYPE, default='x86', null=True, blank=True, max_length=20,
                                   verbose_name=_('Device Type'))  # 设备类型
    snmp_version = models.CharField(choices=SNMP_VERSION, default='2c', null=True, blank=True, max_length=20,
                                   verbose_name=_('SNMP Version'))  # 设备类型
    material = models.ForeignKey(Material, max_length=64, null=True, blank=True, on_delete=models.SET_NULL,
                            verbose_name=_("Material"))
    front_pic_file = models.CharField(max_length=128, null=True, blank=True,
                              verbose_name=_('Front picture file'))# 前部照片
    rear_pic_file = models.CharField(max_length=128, null=True, blank=True,
                              verbose_name=_('Rear picture file')) # 背部照片
    assets = models.ManyToManyField('assets.Asset', related_name='granted_by_visions_classify', blank=True, verbose_name=_("Asset"))
    nodes = models.ManyToManyField('assets.Node', related_name='granted_by_visions_classify', blank=True, verbose_name=_("Nodes"))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_by = models.CharField(max_length=128, blank=True, verbose_name=_('Created by'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    comment = models.TextField(verbose_name=_('Comment'), blank=True)

    objects = ClassifyManager.from_queryset(ClassifyQuerySet)()

    class Meta:
        unique_together = [('org_id', 'name')]
        verbose_name = _("Classify")

    def __str__(self):
        return self.name

    @property
    def id_str(self):
        return str(self.id)

    @property
    def material_name(self):
        return self.material.name

    @property
    def is_valid(self):
        # if self.date_expired > timezone.now() > self.date_start and self.is_active:
        if self.is_active:
            return True
        return False

    def get_all_assets(self):
        assets = set(self.assets.all())
        for node in self.nodes.all():
            _assets = node.get_all_assets()
            set_or_append_attr_bulk(_assets, 'inherit', node.value)
            assets.update(set(_assets))
        return assets

    def to_dict(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = str(getattr(self, field.name))
        return d
