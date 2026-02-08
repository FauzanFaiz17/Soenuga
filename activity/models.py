from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from organization.models import OrganizationUnit
from django.contrib.auth.models import Group


class Event(models.Model):

    TIPE_CHOICES = [
        ('kegiatan', 'Kegiatan'),
        ('acara', 'Acara'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    tipe = models.CharField(
        max_length=20,
        choices=TIPE_CHOICES
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    lokasi = models.CharField(max_length=200)

    gdrive_link = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    def __str__(self):
        return self.name


    # ==========================
    # Validasi tanggal
    # ==========================
    def clean(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    "Tanggal selesai tidak boleh lebih awal dari tanggal mulai."
                )


    # ==========================
    # Status otomatis (opsional)
    # ==========================
    def update_status(self):
        now = timezone.now()

        if self.status == 'cancelled':
            return

        if now < self.start_date:
            self.status = 'upcoming'

        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'

        else:
            self.status = 'completed'

        self.save()


class EventParticipant(models.Model):
    """
    Model untuk menyimpan peserta/panitia pada Event (Acara).
    Setiap peserta memiliki role spesifik seperti Ketua, Sekretaris, Bendahara, dll.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_participations'
    )
    
    role = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_participants',
        help_text="Peran dalam panitia: Ketua, Sekretaris, Bendahara, dll"
    )
    
    is_active = models.BooleanField(default=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        verbose_name = "Event Participant"
        verbose_name_plural = "Event Participants"
    
    def __str__(self):
        role_name = self.role.name if self.role else "Peserta"
        return f"{self.user} - {role_name} @ {self.event.name}"


class ActivityParticipant(models.Model):
    """
    Model untuk menyimpan peserta pada Activity (Kegiatan).
    Peserta bisa berupa individual user atau seluruh unit/departemen.
    """
    
    PARTICIPANT_STATUS = [
        ('hadir', 'Hadir'),
        ('absen', 'Absen'),
        ('izin', 'Izin'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='activity_participants'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_participations'
    )
    
    unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_participations',
        help_text="Jika peserta adalah unit/departemen, isi field ini"
    )
    
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS,
        default='hadir'
    )
    
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        verbose_name = "Activity Participant"
        verbose_name_plural = "Activity Participants"
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def clean(self):
        """Validasi bahwa user dan unit tidak boleh kosong sekaligus"""
        if not self.user and not self.unit:
            raise ValidationError(
                "Peserta harus berupa User atau Unit, tidak boleh kosong keduanya."
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        participant_name = self.user.username if self.user else f"Unit: {self.unit.name}"
        return f"{participant_name} ({self.status}) @ {self.event.name}"
