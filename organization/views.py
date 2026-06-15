from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group,Permission
from django.http import HttpResponseForbidden
from organization.helpers.permissions import has_permission
from collections import defaultdict

from .models import RolePermission, RoleMeta
from .forms import RoleForm

User = get_user_model()



def superadmin_required(user):
    return user.is_superuser

# List & Manage Roles
@login_required
@user_passes_test(superadmin_required)
def role_list(request):
    roles = Group.objects.all()

    role_id = request.GET.get("edit")
    group = None
    role_meta = None

    if role_id:
        group = get_object_or_404(Group, id=role_id)
        role_meta = RoleMeta.objects.filter(role=group).first()

    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            is_leader = form.cleaned_data["is_leader"]

            if request.POST.get("role_id"):
                # EDIT
                group = get_object_or_404(Group, id=request.POST["role_id"])
                group.name = name
                group.save()

                RoleMeta.objects.update_or_create(
                    role=group,
                    defaults={"is_leader": is_leader}
                )
                messages.success(request, "Role berhasil diperbarui")
            else:
                # ADD
                group, _ = Group.objects.get_or_create(name=name)
                RoleMeta.objects.get_or_create(
                    role=group,
                    defaults={"is_leader": is_leader}
                )
                messages.success(request, "Role berhasil dibuat")

            return redirect("role_list")
    else:
        initial = {}
        if group:
            initial = {
                "name": group.name,
                "is_leader": role_meta.is_leader if role_meta else False
            }
        form = RoleForm(initial=initial)

    return render(request, "admin/roles/list.html", {
        "roles": roles,
        "form": form,
        "group": group,
    })


# create role baru
@login_required
@user_passes_test(superadmin_required)
def role_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_leader = request.POST.get('is_leader') == 'on'

        group, created = Group.objects.get_or_create(name=name)
        RoleMeta.objects.get_or_create(
            role=group,
            defaults={'is_leader': is_leader}
        )

        messages.success(request, "Role berhasil dibuat")
        return redirect('role_list')

    return render(request, 'admin/roles/create.html')

# manage role permission + scope

@login_required
@user_passes_test(superadmin_required)
def manage_role_permissions(request, role_id):
    role = get_object_or_404(Group, id=role_id)

    # permissions tetap SATU sumber (ini penting)
    permissions = Permission.objects.filter(
        content_type__app_label__in=["users", "organization","correspondence","inventory"]
    ).select_related("content_type")

    scopes = ["global", "unit", "department", "self"]

    # =========================
    # POST — JANGAN DIUBAH LOGIC-NYA
    # =========================
    if request.method == "POST":
        RolePermission.objects.filter(role=role).delete()

        selected_permissions = request.POST.getlist("permissions")

        for perm in permissions:
            if str(perm.id) in selected_permissions:
                scope = request.POST.get(f"scope_{perm.id}", "global")
                RolePermission.objects.create(
                    role=role,
                    permission=perm,
                    scope=scope
                )

        return redirect("role_list")

    # =========================
    # GET — UNTUK TAMPILAN
    # =========================
    role_permissions = {
        rp.permission_id: rp.scope
        for rp in RolePermission.objects.filter(role=role)
    }

    # grouping KHUSUS tampilan
    grouped_permissions = defaultdict(list)
    for perm in permissions:
        grouped_permissions[perm.content_type.app_label].append(perm)

    return render(request, 'admin/roles/permissions.html', {
        "role": role,
        "grouped_permissions": dict(grouped_permissions),
        "role_permissions": role_permissions,
        "scopes": scopes,
    })






@login_required
def test(request):

    return render(request, 'test.html')


@login_required
def index(request):
    query = request.GET.get('search', '')  # Ambil query search dari input
    user_list = User.objects.all()

    if query:
        user_list = user_list.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(user_list, 10)  # 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'dashboard/index.html' , {
            'users': page_obj,
            'search_query': query,
        })


def list_user(request):
    query = request.GET.get('search', '')  # Ambil query search dari input
    user_list = User.objects.all()

    if query:
        user_list = user_list.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(user_list, 10)  # 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'organization/user.html' , {
            'users': page_obj,
            'search_query': query,
        })