from django.db.models.signals import post_save
from django.dispatch import receiver
from activity.models import ActivityParticipant
from .models import ActivityFine

# Nominal denda sesuai aturan Soenuga
FINE_AMOUNTS = {
    'sakit': 3000,
    'izin':  4000,
    'absen': 5000,
}


@receiver(post_save, sender=ActivityParticipant)
def auto_create_or_update_fine(sender, instance, created, **kwargs):
    """
    Otomatis membuat atau memperbarui ActivityFine setiap kali
    status ActivityParticipant disimpan.

    Aturan:
    - hadir  → hapus denda (jika ada dan belum dibayar)
    - sakit  → denda Rp3.000
    - izin   → denda Rp4.000
    - absen  → denda Rp5.000

    PENTING: ActivityFine yang dibuat di sini TIDAK langsung
    membuat FinancialTransaction. Transaksi baru dibuat di
    service.register_fine_payment() saat bendahara konfirmasi lunas.
    """
    status = instance.status

    if status == 'hadir':
        # Hapus denda jika belum dibayar (misal koreksi absen → hadir)
        ActivityFine.objects.filter(
            participant=instance,
            status='unpaid'
        ).delete()
        return

    amount = FINE_AMOUNTS.get(status)
    if amount is None:
        return

    # Buat atau update denda. Jika sudah paid, jangan overwrite.
    fine, _ = ActivityFine.objects.get_or_create(
        participant=instance,
        defaults={
            'amount': amount,
            'status': 'unpaid',
        }
    )

    # Jika sudah ada tapi belum lunas, update nominal sesuai status baru
    if fine.status == 'unpaid' and fine.amount != amount:
        fine.amount = amount
        fine.save()
