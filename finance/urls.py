from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('financial/',                              views.finance_index,             name='index'),
    path('financial/fee-period/create/',            views.fee_period_create,         name='fee-period-create'),
    path('financial/transaction/create/',           views.manual_transaction_create, name='transaction-create'),
    path('financial/bill/<int:pk>/pay/',            views.bill_pay,                  name='bill-pay'),
    path('financial/fine/<int:pk>/pay/',            views.fine_pay,                  name='fine-pay'),
    path('financial/transaction/<int:pk>/delete/',  views.transaction_delete,        name='transaction-delete'),
]
