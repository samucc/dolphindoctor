# -*- coding: utf-8 -*-
#

from rest_framework import generics
from rest_framework_bulk import BulkModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from ..serializers import MaterialSerializer
from ..models import Material
from common.permissions import IsOrgAdmin
from common.mixins import IDInCacheFilterMixin


__all__ = ['MaterialViewSet']


class MaterialViewSet(IDInCacheFilterMixin, BulkModelViewSet):
    filter_fields = ("name",'video_path','video_name')
    search_fields = filter_fields
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = (IsOrgAdmin,)
    pagination_class = LimitOffsetPagination
