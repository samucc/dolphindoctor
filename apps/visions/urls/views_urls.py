# coding:utf-8

from django.conf.urls import url
from django.urls import path
from .. import views

app_name = 'visions'

urlpatterns = [
    path('video/', views.VideoListView.as_view(), name='vision-video-list'),
    path('video/create/', views.VideoCreateView.as_view(), name='vision-video-create'),
    path('video/<uuid:pk>/update/', views.VideoUpdateView.as_view(), name='vision-video-update'),
    path('video/<uuid:pk>/', views.VideoDetailView.as_view(),name='vision-video-detail'),
    path('video/<uuid:pk>/delete/', views.VideoDeleteView.as_view(), name='vision-video-delete'),
    path('video/update/', views.VideoBulkUpdateView.as_view(), name='video-bulk-update'),


    path('music/', views.MusicListView.as_view(), name='vision-music-list'),
    path('music/create/', views.MusicCreateView.as_view(), name='vision-music-create'),
    path('music/<uuid:pk>/update/', views.MusicUpdateView.as_view(), name='vision-music-update'),
    path('music/<uuid:pk>/', views.MusicDetailView.as_view(),name='vision-music-detail'),
    path('music/<uuid:pk>/delete/', views.MusicDeleteView.as_view(), name='vision-music-delete'),
    path('music/<uuid:pk>/asset/', views.MusicAssetView.as_view(), name='vision-music-asset-list'),

    path('gallery/', views.GalleryListView.as_view(), name='vision-gallery-list'),
    path('gallery/create/', views.GalleryCreateView.as_view(), name='vision-gallery-create'),
    path('gallery/<uuid:pk>/update/', views.GalleryUpdateView.as_view(), name='vision-gallery-update'),
    path('gallery/<uuid:pk>/', views.GalleryDetailView.as_view(),name='vision-gallery-detail'),
    path('gallery/<uuid:pk>/delete/', views.GalleryDeleteView.as_view(), name='vision-gallery-delete'),
    path('gallery/<uuid:pk>/asset/', views.GalleryAssetView.as_view(), name='vision-gallery-asset-list'),

    path('effect/', views.EffectListView.as_view(), name='vision-effect-list'),
    path('effect/create/', views.EffectCreateView.as_view(), name='vision-effect-create'),
    path('effect/<uuid:pk>/update/', views.EffectUpdateView.as_view(), name='vision-effect-update'),
    path('effect/<uuid:pk>/', views.EffectDetailView.as_view(),name='vision-effect-detail'),
    path('effect/<uuid:pk>/delete/', views.EffectDeleteView.as_view(), name='vision-effect-delete'),
    path('effect/update/', views.EffectBulkUpdateView.as_view(), name='effect-bulk-update'),

    path('material/', views.MaterialListView.as_view(), name='vision-material-list'),
    path('material/create/', views.MaterialCreateView.as_view(), name='vision-material-create'),
    path('material/<uuid:pk>/update/', views.MaterialUpdateView.as_view(), name='vision-material-update'),
    path('material/<uuid:pk>/', views.MaterialDetailView.as_view(),name='vision-material-detail'),
    path('material/<uuid:pk>/delete/', views.MaterialDeleteView.as_view(), name='vision-material-delete'),
    path('material/update/', views.MaterialBulkUpdateView.as_view(), name='material-bulk-update'),

    path('video-combine/', views.VideoCombineListView.as_view(), name='vision-video-combine-list'),
    path('video-combine/create/', views.VideoCombineCreateView.as_view(), name='vision-video-combine-create'),
    path('video-combine/<uuid:pk>/update/', views.VideoCombineUpdateView.as_view(), name='vision-video-combine-update'),
    path('video-combine/<uuid:pk>/', views.VideoCombineDetailView.as_view(),name='vision-video-combine-detail'),
    path('video-combine/<uuid:pk>/delete/', views.VideoCombineDeleteView.as_view(), name='vision-video-combine-delete'),
    path('video-combine/<uuid:pk>/asset/', views.VideoCombineAssetView.as_view(), name='vision-video-combine-asset-list'),

    path('classify/', views.ClassifyListView.as_view(), name='vision-classify-list'),
    path('classify/create/', views.ClassifyCreateView.as_view(), name='vision-classify-create'),
    path('classify/<uuid:pk>/update/', views.ClassifyUpdateView.as_view(), name='vision-classify-update'),
    path('classify/<uuid:pk>/', views.ClassifyDetailView.as_view(),name='vision-classify-detail'),
    path('classify/<uuid:pk>/delete/', views.ClassifyDeleteView.as_view(), name='vision-classify-delete'),
    path('classify/<uuid:pk>/asset/', views.ClassifyAssetView.as_view(), name='vision-classify-asset-list'),
]
