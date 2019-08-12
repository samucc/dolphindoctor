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
from visions.models import VideoCombine,Video
from visions.hands import Asset, Node,  NodeSerializer
# from visions.hands import AssetGrantedSerializer, Asset, Node, \
#     NodeGrantedSerializer, NodeSerializer
from orgs.utils import set_to_root_org
from visions import serializers


class VideoCombineViewSet(viewsets.ModelViewSet):
    """
    资产授权列表的增删改查api
    """
    queryset = VideoCombine.objects.all()
    serializer_class = serializers.VideoCombineCreateUpdateSerializer
    vision_classes = (IsOrgAdmin,)

    def get_serializer_class(self):
        if self.action in ("list", 'retrieve'):
            return serializers.VideoCombineListSerializer
        return self.serializer_class
    
    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        videos = self.request.data.get('videos')
        # if videos != []:
        #     videos.update(video_combine=vision)
        #     videos.update(effect=vision.effect)
        #     videos.update(gallery=vision.gallery)
        #     videos.update(music=vision.music)
        # else:
        #     videos.update(video_combine=None)
        #     videos.update(effect=None)
        #     videos.update(gallery=None)
        #     videos.update(music=None)
        super().update(request, *args, **kwargs)
        return Response({"msg": videos})

    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.request.query_params.get('video')
        if not video_id:
            return queryset

        visions = set()
        if video_id:
            video = get_object_or_404(Video, pk=video_id)
            visions = set(queryset.filter(videos=video))
        return visions

class VideoCombineRemoveAssetApi(RetrieveUpdateAPIView):
    """
    将用户从授权中移除，Detail页面会调用
    """
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.VideoCombineUpdateAssetSerializer
    queryset = VideoCombine.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            videos = serializer.validated_data.get('videos')

            video_id_list = [video.id for video in videos]
            if videos:
                vision.videos.remove(*tuple(videos))
                Video.objects.filter(id__in=video_id_list).update(video_combine=None)
                Video.objects.filter(id__in=video_id_list).update(effect=None)
                Video.objects.filter(id__in=video_id_list).update(gallery=None)
                Video.objects.filter(id__in=video_id_list).update(music=None)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})

class VideoCombineAddAssetApi(RetrieveUpdateAPIView):
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.VideoCombineUpdateAssetSerializer
    queryset = VideoCombine.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            videos = serializer.validated_data.get('videos')

            video_id_list = [video.id for video in videos]
            if videos:
                vision.videos.add(*tuple(videos))
                Video.objects.filter(id__in=video_id_list).update(video_combine=vision)
                Video.objects.filter(id__in=video_id_list).update(effect=vision.effect)
                Video.objects.filter(id__in=video_id_list).update(gallery=vision.gallery)
                Video.objects.filter(id__in=video_id_list).update(music=vision.music)

            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})


