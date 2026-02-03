from django.db import models
from django.core.exceptions import ValidationError
from users.models import User
from django.contrib.auth.models import Group,Permission




class ProgramStudi(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    



class MemberProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    npm = models.CharField(max_length=20, unique=True)
    program_studi = models.ForeignKey(
        ProgramStudi,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    angkatan = models.CharField(
        max_length=2,
        help_text="Format dua digit, contoh: 21"
    )
    nomor_anggota = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        db_index=True
    )

    def save(self, *args, **kwargs):
        if self.npm and self.angkatan and self.program_studi:
            last_five_digits = self.npm[-5:]
            new_number = (
                f"{self.program_studi.code}."
                f"{self.angkatan}."
                f"{last_five_digits}"
            )

            # update jika berubah
            if self.nomor_anggota != new_number:
                self.nomor_anggota = new_number

        super().save(*args, **kwargs)


    def clean(self):
        if not self.angkatan.isdigit() or len(self.angkatan) != 2:
            raise ValidationError("Angkatan harus 2 digit angka.")


    def __str__(self):
        return f"{self.user} ({self.nomor_anggota})"

class OrganizationUnit(models.Model):
    UNIT_TYPE = (
        ('department', 'Department'),
        ('division', 'Division'),
    )

    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class Meta:
        unique_together = ('name', 'parent')
        indexes = [
            models.Index(fields=['unit_type']),
        ]



    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def clean(self):
        if self.unit_type == 'department' and self.parent is not None:
            raise ValidationError("Department tidak boleh memiliki parent.")
        if self.unit_type == 'division' and self.parent is None:
            raise ValidationError("Division harus memiliki parent department.")

    def __str__(self):
        return self.name
    

class Role(Group):
    class Meta:
        proxy = True
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class RolePermission(models.Model):
    SCOPE_CHOICES = (
        ('global', 'Global'),
        ('unit', 'Unit'),
        ('department', 'Department'),
        ('self', 'Self'),
    )

    role = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE
    )
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default='global'
    )

    class Meta:
        unique_together = ('role', 'permission', 'scope')

    def __str__(self):
        return f"{self.role.name} - {self.permission.codename} ({self.scope})"


class Membership(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name='memberships'
    )

    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    def clean(self):
        # pastikan RoleMeta ada
        if hasattr(self.role, 'rolemeta') and self.role.rolemeta.is_leader:
            exists = Membership.objects.filter(
                unit=self.unit,
                role=self.role,
                is_active=True
            ).exclude(pk=self.pk).exists()

            if exists:
                raise ValidationError(
                    f"{self.unit} sudah memiliki {self.role.name}"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    class Meta:
        unique_together = ('user', 'unit')

    def __str__(self):
        return f"{self.user} - {self.role} @ {self.unit}"


def user_is_leader(user, unit):
    return Membership.objects.filter(
        user=user,
        unit=unit,
        role__name__in=[
            'Ketua Umum',
            'Kepala Departemen',
            'Kepala Divisi'
        ],
        is_active=True
    ).exists()

def user_can_manage_users(user):
    return Membership.objects.filter(
        user=user,
        role__name__in=[
            'Ketua Umum',
            'Kepala Departemen',
            'Kepala Divisi'
        ],
        is_active=True
    ).exists()

class RoleMeta(models.Model):
    role = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='rolemeta'
    )
    is_leader = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role.name} (leader={self.is_leader})"