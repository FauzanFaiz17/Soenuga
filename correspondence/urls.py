from django.urls import path
from .views import surat, correspondence_create,update_correspondence,delete_correspondence

urlpatterns = [
    path('surat/', surat, name='surat'),
    path('surat-add/', correspondence_create, name='correspondence_create'),
    path('surat/update/<int:pk>/', update_correspondence, name='update_correspondence'),
    path('delete-surat/<int:pk>/', delete_correspondence, name='delete_correspondence'),
    # path('export-surat/', export_pdf, name='export_pdf'),

]