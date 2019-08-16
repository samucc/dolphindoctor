# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from surveys.models import Case
from common.mixins import BulkSerializerMixin
from common.serializers import AdaptedBulkListSerializer
from common.fields import StringManyToManyField


class CaseSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Case
        list_serializer_class = AdaptedBulkListSerializer
        fields = [
            'id', 'org_id', 'date_created','name',
            'created_by','disease_code','case_number','is_active'
        ]
        extra_kwargs = {
            'created_by': {'label': _('Created by'), 'read_only': True}
        }


