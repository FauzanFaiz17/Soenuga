
from django.urls import path
from .views import test, index,list_user ,role_list,role_create,manage_role_permissions

urlpatterns = [
    path('test/', test, name='test'),
    path('dashboard/', index, name='dashboard'),
    path('users/', list_user, name='list_user'),


# khusus admin
    path('adm/roles/', role_list, name='role_list'),
    path('adm/roles/create/', role_create, name='role_create'),
    path('adm/roles/<int:role_id>/permissions/', manage_role_permissions, name='manage_role_permissions'),

]
