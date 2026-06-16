from django import forms
from .models import FeePeriod, Payment,FeeType, MemberBill, FinancialTransaction


class FeePeriodForm(forms.ModelForm):

    class Meta:
        model = FeePeriod

        fields = [
            'fee_type',
            'title',
            'amount',
            'due_date',
            'description'
        ]



class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            'amount',
            'notes'
        ]

class ExpenseForm(forms.ModelForm):

    class Meta:
        model = FinancialTransaction

        fields = [
            'transaction_date',
            'amount',
            'description'
        ]