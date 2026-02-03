from organization.models import Membership, RolePermission
from django.contrib.auth.models import Permission

def has_permission(user, perm_codename, target=None):
    """
    user   = request.user
    target = object target (boleh None)
    """

    if not user.is_authenticated:
        return False

    # superuser bypass
    if user.is_superuser:
        return True

    membership = getattr(user, "active_membership", None)
    if not membership:
        return False

    role = membership.role  # ← Group
    permission = Permission.objects.filter(codename=perm_codename).first()
    if not permission:
        return False

    rp_qs = RolePermission.objects.filter(
        role=role,
        permission=permission
    )

    if not rp_qs.exists():
        return False

    # sementara: scope global dulu
    return True
