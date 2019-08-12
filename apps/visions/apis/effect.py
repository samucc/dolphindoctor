# -*- coding: utf-8 -*-
#

from rest_framework import generics
from rest_framework_bulk import BulkModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from ..serializers import EffectSerializer
from ..models import Effect
from common.permissions import IsOrgAdmin
from common.mixins import IDInCacheFilterMixin


__all__ = ['EffectViewSet']


class EffectViewSet(IDInCacheFilterMixin, BulkModelViewSet):
    filter_fields = ("name",'method')
    search_fields = filter_fields
    queryset = Effect.objects.all()
    serializer_class = EffectSerializer
    permission_classes = (IsOrgAdmin,)
    pagination_class = LimitOffsetPagination
