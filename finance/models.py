from django.db import models
from django.conf import settings
from activity.models import ActivityParticipant


class FeeType(models.Model):

    TYPE_CHOICES = (
        ('kas', 'Kas Bulanan'),
        ('iuran', 'Iuran'),
    )

    name = models.CharField(max_length=100)

    fee_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    default_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FeePeriod(models.Model):

    fee_type = models.ForeignKey(
        FeeType,
        on_delete=models.CASCADE,
        related_name='periods'
    )

    title = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class MemberBill(models.Model):

    STATUS_CHOICES = (
        ('unpaid', 'Belum Bayar'),
        ('partial', 'Sebagian'),
        ('paid', 'Lunas'),
    )

    BILL_TYPES = (
        ('kas', 'Kas'),
        ('iuran', 'Iuran'),
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    fee_period = models.ForeignKey(
        FeePeriod,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    bill_type = models.CharField(
        max_length=20,
        choices=BILL_TYPES,
        default='kas'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'fee_period')

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return f"{self.member} - {self.fee_period}"
    
class Payment(models.Model):

    bill = models.ForeignKey(
        MemberBill,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid_at = models.DateTimeField(auto_now_add=True)

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments'
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bill.member} - {self.amount}"
    
class Receipt(models.Model):

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipts'
    )

    file = models.FileField(
        upload_to='finance/receipts/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


class ActivityFine(models.Model):

    STATUS_CHOICES = (
        ('unpaid', 'Belum Bayar'),
        ('paid', 'Lunas'),
    )

    participant = models.OneToOneField(
        ActivityParticipant,
        on_delete=models.CASCADE,
        related_name='fine'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid'
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.participant.user} - "
            f"{self.participant.event.name}"
        )
    
    @property
    def event_name(self):
        return self.participant.event.name

    @property
    def event_date(self):
        return self.participant.event.start_date

    @property
    def member(self):
        return self.participant.user
    
class FinancialTransaction(models.Model):

    TRANSACTION_TYPES = (
        ('income', 'Pemasukan'),
        ('expense', 'Pengeluaran'),
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    transaction_date = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.TextField()

    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    activity_fine = models.ForeignKey(
        ActivityFine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

