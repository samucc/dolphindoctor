# ~*~ coding: utf-8 ~*~
# 
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveUpdateAPIView,RetrieveAPIView
from rest_framework import viewsets

from common.utils import set_or_append_attr_bulk
from common.permissions import IsValidUser, IsOrgAdmin, IsOrgAdminOrAppUser
from orgs.mixins import RootOrgViewMixin
from visions.models import Music,Gallery,Effect,VideoCombine,Video
from visions.hands import Asset, Node,  NodeSerializer
# from visions.hands import AssetGrantedSerializer, Asset, Node, \
#     NodeGrantedSerializer, NodeSerializer
from orgs.utils import set_to_root_org
from visions import serializers


class MusicViewSet(viewsets.ModelViewSet):
    """
    资产授权列表的增删改查api
    """
    queryset = Music.objects.all()
    serializer_class = serializers.MusicCreateUpdateSerializer
    vision_classes = (IsOrgAdmin,)

    def get_serializer_class(self):
        if self.action in ("list", 'retrieve'):
            return serializers.MusicListSerializer
        return self.serializer_class
    
    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        gallerys = self.request.data.get('gallerys')
        super().update(request, *args, **kwargs)
        return Response({"msg": gallerys})

    def get_queryset(self):
        queryset = super().get_queryset()
        gallery_id = self.request.query_params.get('gallery')
        inherit_nodes = set()
        if not gallery_id:
            return queryset

        visions = set()
        if gallery_id:
            gallery = get_object_or_404(Gallery, pk=gallery_id)
            visions = set(queryset.filter(gallerys=gallery))
        return visions

class MusicRemoveAssetApi(RetrieveUpdateAPIView):
    """
    将用户从授权中移除，Detail页面会调用
    """
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.MusicUpdateAssetSerializer
    queryset = Music.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            gallerys = serializer.validated_data.get('gallerys')
            gallery_id_list, effects = [], []
            for gallery in gallerys:
                effects += gallery.get_all_effects()
                gallery_id_list.append(gallery.id)

            effect_id_list, video_combines = [], []
            for effect in effects:
                video_combines += effect.get_all_video_combines()
                effect_id_list.append(effect.id)

            video_combine_id_list, videos = [], []
            for video_combine in video_combines:
                videos += video_combine.get_all_videos()
                video_combine_id_list.append(video_combine.id)

            video_id_list = [video.id for video in videos]

            if gallerys:
                vision.gallerys.remove(*tuple(gallerys))
                Gallery.objects.filter(id__in=gallery_id_list).update(music=None)
            if effects:
                Effect.objects.filter(id__in=effect_id_list).update(music=None)
            if video_combines:
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(music=None)
            if videos:
                Video.objects.filter(id__in=video_id_list).update(music=None)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})

class MusicAddAssetApi(RetrieveUpdateAPIView):
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.MusicUpdateAssetSerializer
    queryset = Music.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            gallerys = serializer.validated_data.get('gallerys')
            # assets = serializer.validated_data.get('assets')
            gallery_id_list,effects = [],[]
            for gallery in gallerys:
                effects += gallery.get_all_effects()
                gallery_id_list.append(gallery.id)

            effect_id_list,video_combines = [],[]
            for effect in effects:
                video_combines += effect.get_all_video_combines()
                effect_id_list.append(effect.id)

            video_combine_id_list,videos = [],[]
            for video_combine in video_combines:
                videos += video_combine.get_all_videos()
                video_combine_id_list.append(video_combine.id)

            video_id_list = [video.id for video in videos]

            if gallerys:
                vision.gallerys.add(*tuple(gallerys))
                Gallery.objects.filter(id__in=gallery_id_list).update(music=vision)
            if effects:
                Effect.objects.filter(id__in=effect_id_list).update(music=vision)
            if video_combines:
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(music=vision)
            if videos:
                Video.objects.filter(id__in=video_id_list).update(music=vision)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})


