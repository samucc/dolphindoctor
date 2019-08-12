# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from visions.models import VideoCombine
from common.fields import StringManyToManyField


class VideoCombineCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCombine
        exclude = ('created_by', 'date_created')


class VideoCombineListSerializer(serializers.ModelSerializer):
    videos = StringManyToManyField(many=True, read_only=True)
    # inherit = serializers.SerializerMethodField()

    class Meta:
        model = VideoCombine
        # fields = '__all__'
        fields = ['id', 'name','music','gallery','effect','video_quantity','videos',
                  'music_name','gallery_name','effect_name',
                  'is_active','created_by','date_created','comment']

    # @staticmethod
    # def get_inherit(obj):
    #     if hasattr(obj, 'inherit'):
    #         return obj.inherit
    #     else:
    #         return None

class VideoCombineUpdateAssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoCombine
        fields = ['id', 'videos']

