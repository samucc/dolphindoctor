# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from visions.models import Classify
from common.fields import StringManyToManyField


class ClassifyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classify
        exclude = ('created_by', 'date_created')


class ClassifyListSerializer(serializers.ModelSerializer):
    assets = StringManyToManyField(many=True, read_only=True)
    nodes = StringManyToManyField(many=True, read_only=True)
    # inherit = serializers.SerializerMethodField()

    class Meta:
        model = Classify
        # fields = '__all__'
        fields = ['id', 'name','model','height','material_name',
                  'weight','rated_power',
                  'device_type','snmp_version','material',
                  'front_pic_file','rear_pic_file',
                  'assets','nodes',
                  'is_active','created_by','date_created','comment']

    # @staticmethod
    # def get_inherit(obj):
    #     if hasattr(obj, 'inherit'):
    #         return obj.inherit
    #     else:
    #         return None

class ClassifyUpdateAssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classify
        fields = ['id', 'assets']

