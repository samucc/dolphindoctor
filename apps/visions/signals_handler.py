# -*- coding: utf-8 -*-
#
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from common.utils import get_logger
from visions.models import Video


logger = get_logger(__file__)


# @receiver(m2m_changed, sender=Video.nodes.through)
# def on_vision_nodes_changed(sender, instance=None, **kwargs):
#     if isinstance(instance, Video) and kwargs['action'] == 'post_add':
#         logger.debug("Video nodes change signal received")
#         nodes = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
#         system_users = instance.system_users.all()
#         for system_user in system_users:
#             system_user.nodes.add(*tuple(nodes))
#
#
# @receiver(m2m_changed, sender=Video.assets.through)
# def on_vision_assets_changed(sender, instance=None, **kwargs):
#     if isinstance(instance, Video) and kwargs['action'] == 'post_add':
#         logger.debug("Video assets change signal received")
#         assets = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
#         system_users = instance.system_users.all()
#         for system_user in system_users:
#             system_user.assets.add(*tuple(assets))


# @receiver(m2m_changed, sender=Video.system_users.through)
# def on_vision_system_users_changed(sender, instance=None, **kwargs):
#     if isinstance(instance, Video) and kwargs['action'] == 'post_add':
#         logger.debug("Video system_users change signal received")
#         system_users = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
#         assets = instance.assets.all()
#         nodes = instance.nodes.all()
#         for system_user in system_users:
#             system_user.nodes.add(*tuple(nodes))
#             system_user.assets.add(*tuple(assets))
