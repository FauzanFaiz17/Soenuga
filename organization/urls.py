
from django.urls import path
from .views import list_user ,role_list,role_create,manage_role_permissions
from .dashboard import  dashboard

urlpatterns = [


    path('dashboard/', dashboard, name='dashboard'),
    path('users/', list_user, name='list_user'),


# khusus admin
    path('adm/roles/', role_list, name='role_list'),
    path('adm/roles/create/', role_create, name='role_create'),
    path('adm/roles/<int:role_id>/permissions/', manage_role_permissions, name='manage_role_permissions'),

]
