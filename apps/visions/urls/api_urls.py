# coding:utf-8

from django.urls import path
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter
from visions.apis import video,music,gallery,effect,material,video_combine,classify

app_name = 'visions'

# router = routers.DefaultRouter()
router = BulkRouter()
router.register('vision-videos', video.VideoViewSet, 'vision-video')
router.register('vision-musics', music.MusicViewSet, 'vision-music')
router.register('vision-gallerys', gallery.GalleryViewSet, 'vision-gallery')
router.register('vision-effects', effect.EffectViewSet, 'vision-effect')
router.register('vision-materials', material.MaterialViewSet, 'vision-material')
router.register('vision-video-combines', video_combine.VideoCombineViewSet, 'vision-video-combine')
router.register('vision-classifys', classify.ClassifyViewSet, 'vision-classify')


urlpatterns = [
    path('vision-musics/<uuid:pk>/asset/remove/',
         music.MusicRemoveAssetApi.as_view(),
         name='vision-music-remove-gallery'),
    path('vision-musics/<uuid:pk>/asset/add/',
         music.MusicAddAssetApi.as_view(),
         name='vision-music-add-gallery'),

    path('vision-gallerys/<uuid:pk>/asset/remove/',
         gallery.GalleryRemoveAssetApi.as_view(),
         name='vision-gallery-remove-effect'),
    path('vision-gallerys/<uuid:pk>/asset/add/',
         gallery.GalleryAddAssetApi.as_view(),
         name='vision-gallery-add-effect'),
    path('visions-gallerys/<uuid:pk>/asset/list/',
         gallery.GalleryAssetListApi.as_view(), name='vision-gallery-asset-list'),

    path('vision-video-combines/<uuid:pk>/asset/remove/',
         video_combine.VideoCombineRemoveAssetApi.as_view(),
         name='vision-video-combine-remove-asset'),
    path('vision-video-combines/<uuid:pk>/asset/add/',
         video_combine.VideoCombineAddAssetApi.as_view(),
         name='vision-video-combine-add-asset'),

    path('vision-classifys/<uuid:pk>/asset/remove/',
         classify.ClassifyRemoveAssetApi.as_view(),
         name='vision-classify-remove-asset'),
    path('vision-classifys/<uuid:pk>/asset/add/',
         classify.ClassifyAddAssetApi.as_view(),
         name='vision-classify-add-asset'),
    path('visions-classifys/asset/<uuid:pk>/',
         classify.ClassifyListApi.as_view(), name='vision-classify-service-asset'),
]

urlpatterns += router.urls

