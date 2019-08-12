# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from visions.models import Gallery
from common.fields import StringManyToManyField


class GalleryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        exclude = ('created_by', 'date_created')


class GalleryListSerializer(serializers.ModelSerializer):
    effects = StringManyToManyField(many=True, read_only=True)
    # inherit = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        # fields = '__all__'
        fields = ['id', 'name','music','effects',
                  'music_name',
                  'is_active','created_by','date_created','comment']

    # @staticmethod
    # def get_inherit(obj):
    #     if hasattr(obj, 'inherit'):
    #         return obj.inherit
    #     else:
    #         return None

class GalleryUpdateAssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ['id', 'effects']

