from django.db import models

class Inventory(models.Model):

    TIPE_CHOICES = [
        ('consumable', 'Habis'),
        ('asset', 'Aset'),
    ]

    nama = models.CharField(max_length=255)

    tipe = models.CharField(
        max_length=20,
        choices=TIPE_CHOICES,
        default='asset'
    )

    sebelum = models.PositiveIntegerField(default=0)
    ditambah = models.PositiveIntegerField(default=0)

    dipakai = models.PositiveIntegerField(default=0) 
    rusak = models.PositiveIntegerField(default=0)    
    habis = models.PositiveIntegerField(default=0)     

    tanggal = models.DateField()

    keterangan = models.TextField(blank=True, null=True)

    @property
    def sisa(self):
        if self.tipe == 'consumable':
            return self.sebelum + self.ditambah - self.habis

        if self.tipe == 'asset':
            return self.sebelum + self.ditambah - self.rusak

        return 0


class FotoInventory(models.Model):
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='fotos'
    )
    foto = models.ImageField(
        upload_to="foto_inventory/",
        blank=True,
        null=True
    )
