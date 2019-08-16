# coding:utf-8

from django.conf.urls import url
from django.urls import path
from .. import views

app_name = 'surveys'

urlpatterns = [
    path('case/', views.CaseListView.as_view(), name='survey-case-list'),
    path('case/create/', views.CaseCreateView.as_view(), name='survey-case-create'),
    path('case/<uuid:pk>/update/', views.CaseUpdateView.as_view(), name='survey-case-update'),
    path('case/<uuid:pk>/', views.CaseDetailView.as_view(),name='survey-case-detail'),
    path('case/<uuid:pk>/delete/', views.CaseDeleteView.as_view(), name='survey-case-delete'),
    path('case/update/', views.CaseBulkUpdateView.as_view(), name='case-bulk-update'),

]
