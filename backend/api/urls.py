from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, items_view

router = DefaultRouter()
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('items-view/', items_view, name='items-view'),
]
