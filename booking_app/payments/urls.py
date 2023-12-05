# from django.conf.urls import url
from payments import views
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('payments', views.PaymentViewSet)

app_name = 'payments'

urlpatterns = [
    path('', include(router.urls)),
]