
from django.urls import path
from .views import index,role_list,role_create,manage_role_permissions

urlpatterns = [
    path('dashboard/', index, name='dashboard'),


# khusus admin
    path('admin/roles/', role_list, name='role_list'),
    path('admin/roles/create/', role_create, name='role_create'),
    path('admin/roles/<int:role_id>/permissions/', manage_role_permissions, name='manage_role_permissions'),

]
