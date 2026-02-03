from django.db import models

class Correspondence(models.Model):
    JENIS_CHOICES = (
    ('masuk', 'Surat Masuk'),
    ('keluar', 'Surat Keluar'),
    )
    
    nomor = models.CharField(max_length=100)
    perihal = models.CharField(max_length=255)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES)
    tanggal = models.DateField()
    keterangan = models.TextField()
    pengirim = models.CharField(max_length=255)
    file = models.FileField(upload_to='surat/', blank=True, null=True)

    def __str__(self):
        return self.nomor