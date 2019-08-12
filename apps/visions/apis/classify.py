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
from visions.models import Classify
from visions.hands import Asset, Node,  NodeSerializer
# from visions.hands import AssetGrantedSerializer, Asset, Node, \
#     NodeGrantedSerializer, NodeSerializer
from orgs.utils import set_to_root_org
from visions import serializers


class ClassifyViewSet(viewsets.ModelViewSet):
    """
    资产授权列表的增删改查api
    """
    queryset = Classify.objects.all()
    serializer_class = serializers.ClassifyCreateUpdateSerializer
    vision_classes = (IsOrgAdmin,)

    def get_serializer_class(self):
        if self.action in ("list", 'retrieve'):
            return serializers.ClassifyListSerializer
        return self.serializer_class
    
    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        nodes = self.request.data.get('nodes')
        if nodes != []:
           for node_id in nodes:
               node = get_object_or_404(Node, pk=node_id)
               node.get_all_assets().update(classify=vision)
        else:
           for node in vision.nodes.all():
               node.get_all_assets().update(classify=None)
        super().update(request, *args, **kwargs)
        return Response({"msg": nodes})

    def get_queryset(self):
        queryset = super().get_queryset()
        asset_id = self.request.query_params.get('asset')
        node_id = self.request.query_params.get('node')
        inherit_nodes = set()
        if not asset_id and not node_id:
            return queryset

        visions = set()
        if asset_id:
            asset = get_object_or_404(Asset, pk=asset_id)
            visions = set(queryset.filter(assets=asset))
            for node in asset.nodes.all():
                inherit_nodes.update(set(node.get_ancestor(with_self=True)))
        elif node_id:
            node = get_object_or_404(Node, pk=node_id)
            node.get_all_assets().update(classify=None)
            visions = set(queryset.filter(nodes=node))
            inherit_nodes = node.get_ancestor()

        for n in inherit_nodes:
            _visions = queryset.filter(nodes=n)
            set_or_append_attr_bulk(_visions, "inherit", n.value)
            visions.update(_visions)
        return visions

class ClassifyRemoveAssetApi(RetrieveUpdateAPIView):
    """
    将用户从授权中移除，Detail页面会调用
    """
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.ClassifyUpdateAssetSerializer
    queryset = Classify.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            assets = serializer.validated_data.get('assets')
            asset_id_list = []
            for asset in assets:
               asset_id_list.append(asset.id)
            if assets:
                vision.assets.remove(*tuple(assets))
                Asset.objects.filter(id__in=asset_id_list).update(classify=None)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})

class ClassifyAddAssetApi(RetrieveUpdateAPIView):
    vision_classes = (IsOrgAdmin,)
    serializer_class = serializers.ClassifyUpdateAssetSerializer
    queryset = Classify.objects.all()

    def update(self, request, *args, **kwargs):
        vision = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            assets = serializer.validated_data.get('assets')
            asset_id_list = []
            for asset in assets:
               asset_id_list.append(asset.id)
            if assets:
                vision.assets.add(*tuple(assets))
                Asset.objects.filter(id__in=asset_id_list).update(classify=vision)
            return Response({"msg": "ok"})
        else:
            return Response({"error": serializer.errors})


class ClassifyListApi(RetrieveAPIView):
    """
    Get vision by asset
    """
    queryset = Asset.objects.all()
    serializer_class = serializers.ClassifyListSerializer
    permission_classes = (IsOrgAdmin,)

    def retrieve(self, request, *args, **kwargs):
        asset = self.get_object()
        vision_list = []

        classify_ret = Classify.objects.all()
        for classify_item in classify_ret:
            assets = classify_item.get_all_assets()
            if asset not in assets:
                continue

            classify = classify_item
            vision_list.append(classify.to_dict())

        return Response(vision_list)
