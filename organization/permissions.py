from django.contrib.auth.models import Permission
from organization.models import Membership, RolePermission

def has_permission(user, codename, unit=None, target_user=None):
    """
    Cek apakah user punya permission tertentu dengan scope tertentu
    """

    if not user.is_authenticated:
        return False

    # superuser = dewa
    if user.is_superuser:
        return True

    try:
        perm = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return False

    memberships = Membership.objects.filter(
        user=user,
        is_active=True
    ).select_related("role")

    for membership in memberships:
        role = membership.role

        role_perms = RolePermission.objects.filter(
            role=role,
            permission=perm
        )

        for rp in role_perms:
            scope = rp.scope

            # 🌍 GLOBAL
            if scope == "global":
                return True

            # 🏢 UNIT
            if scope == "unit" and unit:
                if membership.unit == unit:
                    return True

            # 🏬 DEPARTMENT
            if scope == "department" and unit:
                if membership.unit == unit or membership.unit == unit.parent:
                    return True

            # 👤 SELF
            if scope == "self" and target_user:
                if user == target_user:
                    return True

    return False
