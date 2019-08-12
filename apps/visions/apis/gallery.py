# ~*~ coding: utf-8 ~*~
# 
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView, Response
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveUpdateAPIView,RetrieveAPIView
from rest_framework import viewsets

from common.utils import set_or_append_attr_bulk
from common.permissions import IsValidUser, IsOrgAdmin, IsOrgAdminOrAppUser
from orgs.mixins import RootOrgViewMixin
from visions.models import Gallery,Effect,VideoCombine,Video
from visions.hands import Asset, Node,  NodeSerializer
# from visions.hands import AssetGrantedSerializer, Asset, Node, \
#     NodeGrantedSerializer, NodeSerializer
from orgs.utils import set_to_root_org
from visions import serializers


class GalleryViewSet(viewsets.ModelViewSet):
    """
    资产授权列表的增删改查api
    """
    queryset = Gallery.objects.all()
    serializer_class = serializers.GalleryCreateUpdateSerializer
    vision_classes = (IsOrgAdmin,)

    def get_serializer_class(self):
        if self.action in ("list", 'retrieve'):
            return serializers.GalleryListSerializer
        return self.serializer_class
    
    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        effects = self.request.data.get('effects')
        super().update(request, *args, **kwargs)
        return Response({"msg": effects})

    def get_queryset(self):
        queryset = super().get_queryset()
        effect_id = self.request.query_params.get('effect')
        inherit_nodes = set()
        if not effect_id:
            return queryset

        visions = set()
        if effect_id:
            effect = get_object_or_404(Node, pk=effect_id)
            visions = set(queryset.filter(effects=effect))
        return visions

class GalleryRemoveAssetApi(RetrieveUpdateAPIView):
    """
    将用户从授权中移除，Detail页面会调用
    """
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.GalleryUpdateAssetSerializer
    queryset = Gallery.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            effects = serializer.validated_data.get('effects')
            effect_id_list, video_combines = [], []
            for effect in effects:
                video_combines += effect.get_all_video_combines()
                effect_id_list.append(effect.id)

            video_combine_id_list, videos = [], []
            for video_combine in video_combines:
                videos += video_combine.get_all_videos()
                video_combine_id_list.append(video_combine.id)

            video_id_list = [video.id for video in videos]

            if effects:
                vision.effects.remove(*tuple(effects))
                Effect.objects.filter(id__in=effect_id_list).update(gallery=None)
                Effect.objects.filter(id__in=effect_id_list).update(music=None)
            if video_combines:
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(gallery=None)
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(music=None)
            if videos:
                Video.objects.filter(id__in=video_id_list).update(gallery=None)
                Video.objects.filter(id__in=video_id_list).update(music=None)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})

class GalleryAddAssetApi(RetrieveUpdateAPIView):
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.GalleryUpdateAssetSerializer
    queryset = Gallery.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            effects = serializer.validated_data.get('effects')
            effect_id_list, video_combines = [], []
            for effect in effects:
                video_combines += effect.get_all_video_combines()
                effect_id_list.append(effect.id)

            video_combine_id_list, videos = [], []
            for video_combine in video_combines:
                videos += video_combine.get_all_videos()
                video_combine_id_list.append(video_combine.id)

            video_id_list = [video.id for video in videos]

            if effects:
                vision.effects.add(*tuple(effects))
                Effect.objects.filter(id__in=effect_id_list).update(gallery=vision)
                Effect.objects.filter(id__in=effect_id_list).update(music=vision.music)
            if video_combines:
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(gallery=vision)
                VideoCombine.objects.filter(id__in=video_combine_id_list).update(music=vision.music)
            if videos:
                Video.objects.filter(id__in=video_id_list).update(gallery=vision)
                Video.objects.filter(id__in=video_id_list).update(music=vision.music)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})

class GalleryAssetListApi(RetrieveAPIView):
    queryset = Gallery.objects.all()
    vision_classes = (IsOrgAdmin,)

    def retrieve(self, request, *args, **kwargs):
        gallery = self.get_object()
        effects = gallery.get_all_effects()
        rows = []  # ['01', '02', '03', '04', '05', '06', '07', '08', '09'];
        columns = []  # ['A', '-', 'B', '-', 'C', '-', 'D', '-', 'E', '-', 'F', '-'];
        video_list = []# ['01_A', '04_A', '07_B', '07_F']
        video_combine_quantity_dict = {}
        for effect in effects:
            videos = effect.get_all_videos()
            video_combines = effect.get_all_video_combines()
            if len(video_combines) == 0:
                video_combines = []
                video_combine_names = []
                for video in videos:
                    if not video.video_combine:
                        continue
                    name = video.video_combine.name
                    if name not in video_combine_names:
                        video_combine_names.append(name)
                        video_combines.append(video.video_combine)
            max_video_quantity = 0 #每一个机柜列最大机柜数量

            for video_combine in video_combines:
                quantity = video_combine.video_quantity #默认一列的数量是17
                name = video_combine.name #列名
                if name not in video_combine_quantity_dict.keys():
                    video_combine_quantity_dict[name] = quantity
                if quantity > max_video_quantity:#保存最大的列数量
                    max_video_quantity = quantity
                columns.append(name)
                # columns.append('-')#每一列中间插入一个空白行


            for quantity_index in range(max_video_quantity):# 生成每一行的编号，按照最大行进行生成
                if (quantity_index+1) < 10:
                    row = "0{}".format(quantity_index+1)
                else:
                    row = "{}".format(quantity_index+1)
                if row not in rows:
                    rows.append(row)


            video_idx_ids = [] # 临时变量
            for idx,video in enumerate(videos):
                group_name = ''
                if video.video_combine:
                    group_name = video.video_combine.name
                video_idx = idx + 1 #默认解析下标
                try:
                    video_idx = int(video.name.split('-')[1])#根据名称的第二位编号进行展示
                    video_idx_ids.append(video_idx)
                except:
                    if video_idx_ids:#如果已有编号，则叠加1
                        video_idx = max(video_idx_ids)+1
                if video_idx < 10:
                    video_id = "0{}_{}".format(video_idx,group_name)
                else:
                    video_id = "{}_{}".format(video_idx,group_name)
                video_list.append({"id":video.id,"mid":video_id})

        columns.sort()#按照生序排列
        new_columns = []
        for idx,column in enumerate(columns):
            new_columns.append(column)
            new_columns.append('-')  # 每一列中间插入一个空白行
        map_list = []
        # map: [ // 座位图
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_',
        #     'c_c_c_c_c_c_'
        # ]
        for idx, row in enumerate(rows):
            row_str = ''
            for column in new_columns:
                if column == '-':
                    row_str += '_'
                    continue
                video_combine_quantity = video_combine_quantity_dict.get(column, 17)
                if idx + 1 > video_combine_quantity:
                    row_str += '_'
                else:
                    row_str += 'c'
            map_list.append(row_str)  # 根据最大行生成每一行的占位
        asset_list = [{"videos":video_list,"maps":map_list,"rows":rows,"columns":new_columns}]#effect.get_all_assets()
        return JsonResponse(asset_list,safe=False)
