# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from visions.models import Effect
from common.mixins import BulkSerializerMixin
from common.serializers import AdaptedBulkListSerializer
from common.fields import StringManyToManyField


class EffectSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Effect
        list_serializer_class = AdaptedBulkListSerializer
        fields = [
            'id', 'org_id', 'name', 'comment', 'date_created',
            'created_by','method','time_duration','start_time','end_time','is_active'
        ]
        extra_kwargs = {
            'created_by': {'label': _('Created by'), 'read_only': True}
        }


