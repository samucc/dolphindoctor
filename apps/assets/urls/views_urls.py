# coding:utf-8
from django.urls import path
from .. import views

app_name = 'assets'

urlpatterns = [
    # Resource asset url
    path('', views.AssetListView.as_view(), name='asset-index'),
    path('asset/', views.AssetListView.as_view(), name='asset-list'),
    path('asset/create/', views.AssetCreateView.as_view(), name='asset-create'),
    path('asset/<uuid:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('asset/<uuid:pk>/update/', views.AssetUpdateView.as_view(), name='asset-update'),
    path('asset/<uuid:pk>/delete/', views.AssetDeleteView.as_view(), name='asset-delete'),
    path('asset/update/', views.AssetBulkUpdateView.as_view(), name='asset-bulk-update'),
    # Asset user view
    path('asset/<uuid:pk>/asset-user/', views.AssetUserListView.as_view(), name='asset-user-list'),

    # User asset view
    path('user-asset/', views.UserAssetListView.as_view(), name='user-asset-list'),

    # Resource admin user url
    path('admin-user/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('admin-user/create/', views.AdminUserCreateView.as_view(), name='admin-user-create'),
    path('admin-user/<uuid:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin-user/<uuid:pk>/update/', views.AdminUserUpdateView.as_view(), name='admin-user-update'),
    path('admin-user/<uuid:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin-user-delete'),
    path('admin-user/<uuid:pk>/assets/', views.AdminUserAssetsView.as_view(), name='admin-user-assets'),

    # Resource system user url
    path('system-user/', views.SystemUserListView.as_view(), name='system-user-list'),
    path('system-user/create/', views.SystemUserCreateView.as_view(), name='system-user-create'),
    path('system-user/<uuid:pk>/', views.SystemUserDetailView.as_view(), name='system-user-detail'),
    path('system-user/<uuid:pk>/update/', views.SystemUserUpdateView.as_view(), name='system-user-update'),
    path('system-user/<uuid:pk>/delete/', views.SystemUserDeleteView.as_view(), name='system-user-delete'),
    path('system-user/<uuid:pk>/asset/', views.SystemUserAssetView.as_view(), name='system-user-asset'),

    path('label/', views.LabelListView.as_view(), name='label-list'),
    path('label/create/', views.LabelCreateView.as_view(), name='label-create'),
    path('label/<uuid:pk>/update/', views.LabelUpdateView.as_view(), name='label-update'),
    path('label/<uuid:pk>/delete/', views.LabelDeleteView.as_view(), name='label-delete'),

    # path('domain/<uuid:pk>/gateway/create/', views.DomainGatewayCreateView.as_view(), name='domain-gateway-create'),
    # path('domain/gateway/<uuid:pk>/update/', views.DomainGatewayUpdateView.as_view(), name='domain-gateway-update'),

]
