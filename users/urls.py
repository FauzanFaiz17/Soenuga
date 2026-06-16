
from django.urls import path
from .views import register, signin, profile_view,upload_avatar,change_password,detail_member
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', signin, name='signin'),
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('upload_avatar/', upload_avatar, name='upload_avatar'),
    path('change_password/', change_password, name='change_password'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('members/<int:user_id>/',detail_member,name='detail_member'),
]
