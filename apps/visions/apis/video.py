# -*- coding: utf-8 -*-
#

from rest_framework import generics
from rest_framework_bulk import BulkModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from ..serializers import VideoSerializer
from ..models import Video
from common.permissions import IsOrgAdmin
from common.mixins import IDInCacheFilterMixin


__all__ = ['VideoViewSet']


class VideoViewSet(IDInCacheFilterMixin, BulkModelViewSet):
    filter_fields = ("name",'category','show','show_time')
    search_fields = filter_fields
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (IsOrgAdmin,)
    pagination_class = LimitOffsetPagination
