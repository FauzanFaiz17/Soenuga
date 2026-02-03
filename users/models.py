from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    foto_profil = models.ImageField(upload_to='profile/', null=True, blank=True)
    nomor_telepon = models.CharField(max_length=15, blank=True)
    
    @property
    def active_membership(self):
        return self.memberships.filter(is_active=True).first()

    def __str__(self):
        return self.get_full_name() or self.username