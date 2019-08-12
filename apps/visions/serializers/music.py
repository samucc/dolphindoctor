# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from visions.models import Music
from common.fields import StringManyToManyField


class MusicCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        exclude = ('created_by', 'date_created')


class MusicListSerializer(serializers.ModelSerializer):
    gallerys = StringManyToManyField(many=True, read_only=True)
    inherit = serializers.SerializerMethodField()

    class Meta:
        model = Music
        fields = '__all__'

    @staticmethod
    def get_inherit(obj):
        if hasattr(obj, 'inherit'):
            return obj.inherit
        else:
            return None

class MusicUpdateAssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Music
        fields = ['id', 'gallerys']

