from users.models import User
from .models import MemberBill,FeeType, FeePeriod,Payment, FinancialTransaction
from django.utils import timezone
from datetime import date
from django.db import transaction


def generate_member_bills(period):

    members = User.objects.filter(
        memberships__is_active=True
    ).distinct()

    bills = []

    for member in members:
        bills.append(
            MemberBill(
                member=member,
                fee_period=period,
                amount=period.amount
            )
        )

    MemberBill.objects.bulk_create(
        bills,
        ignore_conflicts=True
    )

def create_fine_bill(
    member,
    amount,
    title,
    creator
):
    fee_type = FeeType.objects.get(
        fee_type='denda'
    )

    period = FeePeriod.objects.create(
        fee_type=fee_type,
        title=title,
        amount=amount,
        due_date=date.today(),
        created_by=creator
    )

    MemberBill.objects.create(
        member=member,
        fee_period=period,
        amount=amount
    )


@transaction.atomic
def register_payment(
    bill,
    amount,
    receiver,
    notes=''
):

    payment = Payment.objects.create(
        bill=bill,
        amount=amount,
        received_by=receiver,
        notes=notes
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
        description=f"Pembayaran {bill.fee_period.title}",
        payment=payment,
        created_by=receiver
    )

    return payment