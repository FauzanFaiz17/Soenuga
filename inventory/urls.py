from django.urls import path
from django.contrib.auth import views as auth_views
from .views import inventaris_list, inventaris_add, delete_foto, inventory_update,delete_inventory


urlpatterns = [

    path('inventory/', inventaris_list, name='inventory'),
    path('inventaris_add/', inventaris_add, name='inventaris_add'),
    path('update/<int:pk>/', inventory_update, name='inventory_update'),
    path('delete-foto/<int:pk>/', delete_foto, name='delete_foto'),
    path('delete-inventory/<int:pk>/', delete_inventory, name='delete_inventory'),

]
