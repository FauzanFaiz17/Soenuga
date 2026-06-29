from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

from .models import (
    MemberBill, FeePeriod, Payment,
    FinancialTransaction, ActivityFine,
)

User = get_user_model()


# ── Generate tagihan untuk semua anggota aktif ────────────────
def generate_member_bills(period):
    """Dipanggil saat FeePeriod baru dibuat."""
    members = User.objects.filter(
        memberships__is_active=True
    ).distinct()

    bills = [
        MemberBill(
            member=member,
            fee_period=period,
            bill_type=period.fee_type.fee_type,
            amount=period.amount,
        )
        for member in members
    ]
    MemberBill.objects.bulk_create(bills, ignore_conflicts=True)


# ── Catat pembayaran tagihan kas/iuran ───────────────────────
@transaction.atomic
def register_payment(bill, amount, receiver, notes=''):
    payment = Payment.objects.create(
        bill=bill,
        amount=amount,
        received_by=receiver,
        notes=notes,
    )

    bill.paid_amount += amount
    if bill.paid_amount >= bill.amount:
        bill.status = 'paid'
    elif bill.paid_amount > 0:
        bill.status = 'partial'
    bill.save()

    FinancialTransaction.objects.create(
        transaction_type='income',
        transaction_date=timezone.now().date(),
        amount=amount,
        description=(
            f"Pembayaran {bill.fee_period.title} — "
            f"{bill.member.get_full_name() or bill.member.username}"
        ),
        payment=payment,
        created_by=receiver,
    )
    return payment


# ── Catat pembayaran denda (support cicil) ───────────────────
@transaction.atomic
def register_fine_payment(fine, amount, receiver, notes=''):
    """
    Mendukung pembayaran cicil:
    - fine.paid_amount (tambahkan field ini jika belum ada, atau
      hitung dari sum FinancialTransaction terkait fine ini)
    - Jika total bayar sudah >= fine.amount → status = paid
    - Setiap pembayaran (termasuk cicilan) langsung masuk
      FinancialTransaction sebagai income.
    """
    # Hitung sudah berapa yang dibayar sebelumnya
    already_paid = (
        FinancialTransaction.objects
        .filter(activity_fine=fine)
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    remaining = fine.amount - already_paid

    # Jangan bayar melebihi sisa
    pay_amount = min(amount, remaining)

    FinancialTransaction.objects.create(
        transaction_type='income',
        transaction_date=timezone.now().date(),
        amount=pay_amount,
        description=(
            f"Denda {fine.participant.get_status_display()} — "
            f"{fine.member.get_full_name() or fine.member.username} "
            f"@ {fine.event_name}"
            + (f" (cicilan)" if already_paid > 0 else "")
        ),
        activity_fine=fine,
        created_by=receiver,
    )

    new_total = already_paid + pay_amount
    if new_total >= fine.amount:
        fine.status  = 'paid'
        fine.paid_at = timezone.now()
        fine.notes   = notes
        fine.save()

    return pay_amount


# ── Catat transaksi manual (pemasukan/pengeluaran) ────────────
@transaction.atomic
def register_manual_transaction(transaction_type, amount, description,
                                 transaction_date, created_by):
    return FinancialTransaction.objects.create(
        transaction_type=transaction_type,
        transaction_date=transaction_date,
        amount=amount,
        description=description,
        created_by=created_by,
    )
