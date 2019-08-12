# coding: utf-8

from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from django.db.models import Q

from common.utils import get_logger
from visions.models import Video
from .hands import Node

logger = get_logger(__file__)


class Tree:
    def __init__(self):
        self.__all_nodes = Node.objects.all().prefetch_related('assets')
        self.__node_asset_map = defaultdict(set)
        self.nodes = defaultdict(dict)
        self.root = Node.root()
        self.init_node_asset_map()

    def init_node_asset_map(self):
        for node in self.__all_nodes:
            assets = [a.id for a in node.assets.all()]
            for asset in assets:
                self.__node_asset_map[str(asset)].add(node)

    def add_asset(self, asset, system_users):
        nodes = self.__node_asset_map.get(str(asset.id), [])
        self.add_nodes(nodes)
        for node in nodes:
            self.nodes[node][asset].update(system_users)

    def add_node(self, node):
        if node in self.nodes:
            return
        else:
            self.nodes[node] = defaultdict(set)
        if node.key == self.root.key:
            return
        parent_key = ':'.join(node.key.split(':')[:-1])
        for n in self.__all_nodes:
            if n.key == parent_key:
                self.add_node(n)
                break

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)


def get_videos(asset, include_node=True):
    if include_node:
        nodes = asset.get_all_nodes(flat=True)
        arg = Q(assets=asset) | Q(nodes__in=nodes)
    else:
        arg = Q(assets=asset)
    return Video.objects.all().valid().filter(arg)


def get_node_visions(node):
    return Video.objects.all().valid().filter(nodes=node)


class VideoUtil:
    get_visions_map = {
        "Asset": get_videos,
        "Node": get_node_visions,
    }

    def __init__(self, obj):
        self.object = obj
        self._visions = None
        self._assets = None

    @property
    def visions(self):
        if self._visions:
            return self._visions
        object_cls = self.object.__class__.__name__
        func = self.get_visions_map[object_cls]
        visions = func(self.object)
        self._visions = visions
        return visions

    def get_nodes_direct(self):
        """
        返回用户/组授权规则直接关联的节点
        :return: {node1: set(system_user1,)}
        """
        nodes = defaultdict(set)
        visions = self.visions.prefetch_related('nodes', 'system_users')
        for vision in visions:
            for node in vision.nodes.all():
                nodes[node].update(vision.system_users.all())
        return nodes

    def get_assets_direct(self):
        """
        返回用户授权规则直接关联的资产
        :return: {asset1: set(system_user1,)}
        """
        assets = defaultdict(set)
        visions = self.visions.prefetch_related('assets', 'system_users')
        for vision in visions:
            for asset in vision.assets.all().valid().prefetch_related('nodes'):
                assets[asset].update(vision.system_users.all())
        return assets

    def get_assets(self):
        if self._assets:
            return self._assets
        assets = self.get_assets_direct()
        nodes = self.get_nodes_direct()
        for node, system_users in nodes.items():
            _assets = node.get_all_assets().valid().prefetch_related('nodes')
            for asset in _assets:
                assets[asset].update(system_users)
        self._assets = assets
        return self._assets

    def get_nodes_with_assets(self):
        """
        返回节点并且包含资产
        {"node": {"assets": set("system_user")}}
        :return:
        """
        assets = self.get_assets()
        tree = Tree()
        for asset, system_users in assets.items():
            tree.add_asset(asset, system_users)
        return tree.nodes


