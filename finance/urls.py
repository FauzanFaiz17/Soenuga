from django.urls import path
from .views import FinanceDashboardView

urlpatterns = [
    path(
        "financial/",
        FinanceDashboardView.as_view(),
        name="finance"
    ),
]
