from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import (
    FeePeriod,
    MemberBill,
    FinancialTransaction,
    ActivityFine
)
from django.views.generic import TemplateView
from .forms import FeePeriodForm, PaymentForm, ExpenseForm
from .service import generate_member_bills,register_payment
from django.views.generic import ListView, View



class FinanceDashboardView(TemplateView):
    template_name = "finance/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["fee_periods"] = FeePeriod.objects.order_by("-created_at")[:5]

        context["recent_transactions"] = (
            FinancialTransaction.objects
            .order_by("-created_at")[:10]
        )

        context["unpaid_bills"] = (
            MemberBill.objects
            .filter(status="unpaid")
            .select_related(
                "member",
                "fee_period"
            )[:10]
        )

        context["activity_fines"] = (
            ActivityFine.objects
            .select_related(
                "participant",
                "participant__user",
                "participant__event"
            )
            .order_by("-created_at")[:10]
        )

        return context
    



    
class FeePeriodCreateView(CreateView):

    model = FeePeriod

    form_class = FeePeriodForm

    template_name = 'finance/fee_form.html'

    success_url = reverse_lazy(
        'finance:fee-list'
    )

    def form_valid(self, form):

        form.instance.created_by = self.request.user

        response = super().form_valid(form)

        generate_member_bills(self.object)

        return response
    

class BillListView(ListView):

    model = MemberBill

    template_name = 'finance/bill_list.html'

    paginate_by = 25

    queryset = (
        MemberBill.objects
        .select_related(
            'member',
            'fee_period'
        )
    )

class BillPaymentView(View):

    def post(self, request, pk):

        bill = get_object_or_404(
            MemberBill,
            pk=pk
        )

        form = PaymentForm(
            request.POST
        )

        if form.is_valid():

            register_payment(
                bill=bill,
                amount=form.cleaned_data['amount'],
                receiver=request.user,
                notes=form.cleaned_data['notes']
            )

        return redirect(
            'finance:bill-list'
        )