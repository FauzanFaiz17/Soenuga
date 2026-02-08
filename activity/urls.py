from django.urls import path
from django.contrib.auth import views as auth_views
from .views import event_list,event_detail, event_delete, event_add, event_edit,event_participant_add,event_participant_delete,activity_participant_add,activity_participant_edit,activity_participant_delete


urlpatterns = [
        # Event (Acara/Kegiatan)
    path('', event_list, name='event_list'),
    path('add/', event_add, name='event_add'),
    path('<int:pk>/', event_detail, name='event_detail'),
    path('<int:pk>/edit/', event_edit, name='event_edit'),
    path('<int:pk>/delete/', event_delete, name='event_delete'),

    # Event Participants (Panitia Acara)
    path('<int:event_pk>/participant/add/', event_participant_add, name='event_participant_add'),
    path('participant/<int:pk>/delete/', event_participant_delete, name='event_participant_delete'),

    # Activity Participants (Peserta Kegiatan)
    path('<int:event_pk>/activity-participant/add/', activity_participant_add, name='activity_participant_add'),
    path('activity-participant/<int:pk>/edit/', activity_participant_edit, name='activity_participant_edit'),
    path('activity-participant/<int:pk>/delete/', activity_participant_delete, name='activity_participant_delete'),
]