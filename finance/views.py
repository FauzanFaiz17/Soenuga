import json
from decimal import Decimal
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_POST

from django.db.models.functions import TruncMonth
from datetime import timedelta

from .models import (
    FeePeriod, MemberBill, FinancialTransaction,
    ActivityFine, FeeType, Payment,
)
from .forms import (
    FeePeriodForm, PaymentForm, ManualTransactionForm, ActivityFinePayForm,
)
from .service import (
    generate_member_bills, register_payment,
    register_fine_payment, register_manual_transaction,
)


# ── Helper: redirect dengan anchor ───────────────────────────
def _redirect_to(anchor=''):
    url = reverse('finance:index')
    if anchor:
        url += f'#{anchor}'
    return HttpResponseRedirect(url)


# ── Ringkasan keuangan ────────────────────────────────────────
def _get_summary():
    total_income = (
        FinancialTransaction.objects
        .filter(transaction_type='income')
        .aggregate(t=Sum('amount'))['t'] or Decimal('0')
    )
    total_expense = (
        FinancialTransaction.objects
        .filter(transaction_type='expense')
        .aggregate(t=Sum('amount'))['t'] or Decimal('0')
    )
    total_unpaid_bills = (
        MemberBill.objects
        .filter(status__in=['unpaid', 'partial'])
        .aggregate(sisa=Sum('amount') - Sum('paid_amount'))['sisa'] or Decimal('0')
    )
    total_fine_unpaid = (
        ActivityFine.objects
        .filter(status='unpaid')
        .aggregate(t=Sum('amount'))['t'] or Decimal('0')
    )
    return {
        'total_income':       total_income,
        'total_expense':      total_expense,
        'saldo':              total_income - total_expense,
        'total_unpaid_bills': total_unpaid_bills,
        'total_fine_unpaid':  total_fine_unpaid,
    }


# ── Data chart 6 bulan terakhir ───────────────────────────────
def _get_chart_data():
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    # =====================
    # CHART: Transaksi Keuangan per Bulan (6 bulan terakhir)
    # =====================
    six_months_ago = today - timedelta(days=180)
    monthly_income = (
        FinancialTransaction.objects
        .filter(transaction_type='income', transaction_date__gte=six_months_ago)
        .annotate(month=TruncMonth('transaction_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_expense = (
        FinancialTransaction.objects
        .filter(transaction_type='expense', transaction_date__gte=six_months_ago)
        .annotate(month=TruncMonth('transaction_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # build months label
    months_labels = []
    income_data = []
    expense_data = []
    income_map = {row['month'].strftime('%Y-%m'): float(row['total']) for row in monthly_income}
    expense_map = {row['month'].strftime('%Y-%m'): float(row['total']) for row in monthly_expense}
    for i in range(5, -1, -1):
        d = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        key = d.strftime('%Y-%m')
        label = d.strftime('%b %Y')
        months_labels.append(label)
        income_data.append(income_map.get(key, 0))
        expense_data.append(expense_map.get(key, 0))

    # Total keuangan bulan ini
    pemasukan_bulan_ini = FinancialTransaction.objects.filter(
        transaction_type='income', transaction_date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    pengeluaran_bulan_ini = FinancialTransaction.objects.filter(
        transaction_type='expense', transaction_date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    saldo = pemasukan_bulan_ini - pengeluaran_bulan_ini

  
    context = {
        # keuangan
        'pemasukan_bulan_ini': pemasukan_bulan_ini,
        'pengeluaran_bulan_ini': pengeluaran_bulan_ini,
        'saldo': saldo,
   

        # chart data (json)
        'months_labels_json': months_labels,
        'income_data_json': income_data,
        'expense_data_json': expense_data,

    }

    return context
    


# ── Akumulasi tagihan per anggota ─────────────────────────────
def _get_member_summary(filter_type=None, filter_period_id=None):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    members = User.objects.filter(
        memberships__is_active=True
    ).distinct().order_by('first_name', 'username')

    result = []
    for member in members:
        bill_qs = MemberBill.objects.filter(member=member)
        if filter_period_id:
            bill_qs = bill_qs.filter(fee_period_id=filter_period_id)
        elif filter_type:
            bill_qs = bill_qs.filter(bill_type=filter_type)

        bill_agg      = bill_qs.aggregate(total=Sum('amount'), paid=Sum('paid_amount'))
        bill_total    = bill_agg['total'] or Decimal('0')
        bill_paid     = bill_agg['paid']  or Decimal('0')
        bill_remaining = bill_total - bill_paid

        fine_qs        = ActivityFine.objects.filter(participant__user=member)
        fine_total     = fine_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        fine_paid      = (
            FinancialTransaction.objects
            .filter(activity_fine__in=fine_qs)
            .aggregate(t=Sum('amount'))['t'] or Decimal('0')
        )
        fine_remaining = fine_total - fine_paid

        grand_total     = bill_total + fine_total
        grand_paid      = bill_paid  + fine_paid
        grand_remaining = grand_total - grand_paid

        if grand_remaining <= 0:
            status = 'paid'
        elif grand_paid > 0:
            status = 'partial'
        else:
            status = 'unpaid'

        result.append({
            'member':          member,
            'bill_remaining':  bill_remaining,
            'fine_remaining':  fine_remaining,
            'grand_total':     grand_total,
            'grand_paid':      grand_paid,
            'grand_remaining': grand_remaining,
            'fine_total':      fine_total,
            'status':          status,
            'unpaid_bills':    list(
                MemberBill.objects
                .filter(member=member, status__in=['unpaid', 'partial'])
                .select_related('fee_period')
                .order_by('created_at')
            ),
            'unpaid_fines':    list(
                ActivityFine.objects
                .filter(participant__user=member, status='unpaid')
                .select_related('participant__event')
                .order_by('created_at')
            ),
        })
    return result


# ════════════════════════════════════════════════════════════
# VIEW UTAMA
# ════════════════════════════════════════════════════════════
@login_required
def finance_index(request):
    filter_type      = request.GET.get('type')
    filter_period_id = request.GET.get('period')
    page_number      = request.GET.get('page', 1)

    trx_qs = (
        FinancialTransaction.objects
        .select_related(
            'created_by',
            'payment__bill__member',
            'activity_fine__participant__user',
            'activity_fine__participant__event',
        )
        .order_by('-transaction_date', '-created_at')
    )
    paginator    = Paginator(trx_qs, 10)
    transactions = paginator.get_page(page_number)

    member_summaries = _get_member_summary(
        filter_type=filter_type,
        filter_period_id=filter_period_id,
    )

    footer_totals = {
        'grand_total':     sum(m['grand_total']     for m in member_summaries),
        'grand_paid':      sum(m['grand_paid']      for m in member_summaries),
        'grand_remaining': sum(m['grand_remaining'] for m in member_summaries),
    }

    periods = FeePeriod.objects.order_by('-created_at')
    selected_period = None
    if filter_period_id:
        selected_period = FeePeriod.objects.filter(pk=filter_period_id).first()

    context = {
        'segment': 'finance',
        **_get_summary(),
        **_get_chart_data(),
        'transactions':     transactions,
        'member_summaries': member_summaries,
        'footer_totals':    footer_totals,
        'periods':          periods,
        'selected_period':  selected_period,
        'filter_type':      filter_type,
        'filter_period_id': filter_period_id,
        'fee_period_form':  FeePeriodForm(),
        'manual_trx_form':  ManualTransactionForm(
            initial={'transaction_date': timezone.now().date()}
        ),
        'payment_form':     PaymentForm(),
        'fine_pay_form':    ActivityFinePayForm(),
    }
    return render(request, 'finance/index.html', context)


# ── Buat Periode Kas / Iuran ──────────────────────────────────
@login_required
@require_POST
def fee_period_create(request):
    form = FeePeriodForm(request.POST)
    if form.is_valid():
        period = form.save(commit=False)
        period.created_by = request.user
        period.save()
        generate_member_bills(period)
        messages.success(
            request,
            f'Periode "{period.title}" dibuat. '
            f'Tagihan otomatis dibuat untuk semua anggota aktif.'
        )
    else:
        for errors in form.errors.values():
            for e in errors:
                messages.error(request, e)
    return _redirect_to('section-tagihan')


# ── Buat Transaksi Manual ─────────────────────────────────────
@login_required
@require_POST
def manual_transaction_create(request):
    form = ManualTransactionForm(request.POST)
    if form.is_valid():
        register_manual_transaction(
            transaction_type=form.cleaned_data['transaction_type'],
            amount=form.cleaned_data['amount'],
            description=form.cleaned_data['description'],
            transaction_date=form.cleaned_data['transaction_date'],
            created_by=request.user,
        )
        label = 'Pemasukan' if form.cleaned_data['transaction_type'] == 'income' else 'Pengeluaran'
        messages.success(request, f'{label} berhasil dicatat.')
    else:
        for errors in form.errors.values():
            for e in errors:
                messages.error(request, e)
    return _redirect_to('section-transaksi')


# ── Bayar Tagihan Kas / Iuran ─────────────────────────────────
@login_required
@require_POST
def bill_pay(request, pk):
    bill       = get_object_or_404(MemberBill, pk=pk)
    amount_str = request.POST.get('amount', '0').replace(',', '').replace('.', '').strip()
    notes      = request.POST.get('notes', '')

    try:
        amount = Decimal(amount_str)
    except Exception:
        messages.error(request, 'Jumlah pembayaran tidak valid.')
        return _redirect_to('section-tagihan')

    if amount <= 0:
        messages.error(request, 'Jumlah harus lebih dari 0.')
        return _redirect_to('section-tagihan')

    remaining = bill.amount - bill.paid_amount
    if amount > remaining:
        messages.error(
            request,
            f'Jumlah melebihi sisa tagihan (Rp{remaining:,.0f}).'
        )
        return _redirect_to('section-tagihan')

    register_payment(bill, amount, request.user, notes)
    messages.success(
        request,
        f'Pembayaran Rp{amount:,.0f} untuk '
        f'{bill.member.get_full_name() or bill.member.username} berhasil.'
    )
    return _redirect_to('section-tagihan')


# ── Bayar Denda ───────────────────────────────────────────────
@login_required
@require_POST
def fine_pay(request, pk):
    fine       = get_object_or_404(ActivityFine, pk=pk)
    amount_str = request.POST.get('amount', '0').replace(',', '').replace('.', '').strip()
    notes      = request.POST.get('notes', '')

    if fine.status == 'paid':
        messages.warning(request, 'Denda ini sudah lunas.')
        return _redirect_to('section-tagihan')

    try:
        amount = Decimal(amount_str)
    except Exception:
        messages.error(request, 'Jumlah pembayaran tidak valid.')
        return _redirect_to('section-tagihan')

    if amount <= 0:
        messages.error(request, 'Jumlah harus lebih dari 0.')
        return _redirect_to('section-tagihan')

    paid = register_fine_payment(fine, amount, request.user, notes)
    messages.success(
        request,
        f'Pembayaran denda Rp{paid:,.0f} untuk '
        f'{fine.member.get_full_name() or fine.member.username} berhasil dicatat.'
    )
    return _redirect_to('section-tagihan')


# ── Hapus Transaksi Manual ────────────────────────────────────
@login_required
@require_POST
def transaction_delete(request, pk):
    trx = get_object_or_404(
        FinancialTransaction, pk=pk,
        payment__isnull=True,
        activity_fine__isnull=True,
    )
    trx.delete()
    messages.success(request, 'Transaksi berhasil dihapus.')
    return _redirect_to('section-transaksi')
