from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import  OrganizationUnit

User = get_user_model()

from django.db.models.functions import TruncMonth
from finance.models import FinancialTransaction, MemberBill
from activity.models import Event, ActivityParticipant
from correspondence.models import Correspondence
from inventory.models import Inventory

from datetime import timedelta
from django.utils import timezone

def superadmin_required(user):
    return user.is_superuser






@login_required
def dashboard(request):
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)

    # =====================
    # STAT CARDS
    # =====================
    total_anggota = User.objects.filter(is_active=True).count()
    anggota_bulan_ini = User.objects.filter(date_joined__date__gte=this_month_start).count()
    anggota_bulan_lalu = User.objects.filter(
        date_joined__date__gte=last_month_start,
        date_joined__date__lte=last_month_end
    ).count()
    anggota_growth = round(
        ((anggota_bulan_ini - anggota_bulan_lalu) / anggota_bulan_lalu * 100) if anggota_bulan_lalu > 0 else 0, 1
    )

    total_event = Event.objects.count()
    event_bulan_ini = Event.objects.filter(created_at__date__gte=this_month_start).count()
    event_bulan_lalu = Event.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end
    ).count()
    event_growth = round(
        ((event_bulan_ini - event_bulan_lalu) / event_bulan_lalu * 100) if event_bulan_lalu > 0 else 0, 1
    )

    total_inventory = Inventory.objects.count()
    total_surat = Correspondence.objects.count()

    # =====================
    # STATISTIK KEHADIRAN BULAN INI (untuk chart)
    # =====================
    kehadiran_stats = ActivityParticipant.objects.filter(
        event__start_date__date__gte=this_month_start
    ).values('status').annotate(total=Count('id'))
    kehadiran_map = {k['status']: k['total'] for k in kehadiran_stats}
    kehadiran_hadir = kehadiran_map.get('hadir', 0)
    kehadiran_absen = kehadiran_map.get('absen', 0)
    kehadiran_izin = kehadiran_map.get('izin', 0)
    kehadiran_sakit = kehadiran_map.get('sakit', 0)

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

    # =====================
    # TOP ACARA (by participant count)
    # =====================
    top_acara = (
        Event.objects
        .filter(tipe='acara')
        .annotate(peserta_count=Count('participants'))
        .order_by('-peserta_count')[:5]
    )

    # =====================
    # TOP KEGIATAN (by attendance count)
    # =====================
    top_kegiatan = (
        Event.objects
        .filter(tipe='kegiatan')
        .annotate(hadir_count=Count('activity_participants', filter=Q(activity_participants__status='hadir')))
        .order_by('-hadir_count')[:5]
    )

    # =====================
    # UPCOMING EVENTS
    # =====================
    upcoming_events = Event.objects.filter(
        status__in=['upcoming', 'ongoing']
    ).order_by('start_date')[:5]

    # =====================
    # STATUS KEUANGAN ANGGOTA
    # =====================
    tagihan_lunas = MemberBill.objects.filter(status='paid').count()
    tagihan_belum = MemberBill.objects.filter(status='unpaid').count()
    tagihan_sebagian = MemberBill.objects.filter(status='partial').count()

    # =====================
    # DISTRIBUSI UNIT ORGANISASI
    # =====================
    unit_distribution = (
        OrganizationUnit.objects
        .annotate(member_count=Count('memberships', filter=Q(memberships__is_active=True)))
        .filter(unit_type='department')
        .order_by('-member_count')[:5]
    )
    unit_labels = [u.name for u in unit_distribution]
    unit_counts = [u.member_count for u in unit_distribution]

    context = {
        # stat cards
        'total_anggota': total_anggota,
        'anggota_growth': anggota_growth,
        'anggota_bulan_ini': anggota_bulan_ini,
        'total_event': total_event,
        'event_growth': event_growth,
        'total_inventory': total_inventory,
        'total_surat': total_surat,

        # keuangan
        'pemasukan_bulan_ini': pemasukan_bulan_ini,
        'pengeluaran_bulan_ini': pengeluaran_bulan_ini,
        'saldo': saldo,
        'tagihan_lunas': tagihan_lunas,
        'tagihan_belum': tagihan_belum,
        'tagihan_sebagian': tagihan_sebagian,

        # kehadiran
        'kehadiran_hadir': kehadiran_hadir,
        'kehadiran_absen': kehadiran_absen,
        'kehadiran_izin': kehadiran_izin,
        'kehadiran_sakit': kehadiran_sakit,

        # chart data (json)
        'months_labels_json': months_labels,
        'income_data_json': income_data,
        'expense_data_json': expense_data,

        'unit_labels_json': unit_labels,
        'unit_counts_json': unit_counts,

        # lists
        'top_acara': top_acara,
        'top_kegiatan': top_kegiatan,
        'upcoming_events': upcoming_events,
    }

    return render(request, 'dashboard/index.html', context)


def list_user(request):
    query = request.GET.get('search', '')
    user_list = User.objects.all()

    if query:
        user_list = user_list.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'organization/user.html', {
        'users': page_obj,
        'search_query': query,
    })