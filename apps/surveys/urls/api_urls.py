# coding:utf-8

from django.urls import path
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter
from surveys.apis import case

app_name = 'surveys'

# router = routers.DefaultRouter()
router = BulkRouter()
router.register('survey-cases', case.CaseViewSet, 'survey-case')


urlpatterns = [

    path('survey-cases/answer/', case.answer,name='survey-case-answer'),
    path('survey-cases/bodyindex/', case.bodyindex,name='survey-case-bodyindex'),
]

urlpatterns += router.urls

