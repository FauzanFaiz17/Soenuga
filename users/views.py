# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm, SigninForm, UserForm, MemberProfileForm,MembershipForm,MemberUserForm
from .models import  User
from organization.models import MemberProfile, Membership, Role, OrganizationUnit, ProgramStudi
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Program Studi RPL (ID = 2)
            program_studi = ProgramStudi.objects.get(
                name='Rekayasa Perangkat Lunak'
            )

            MemberProfile.objects.create(
                user=user,
                npm=form.cleaned_data['npm'],
                program_studi=program_studi,
                angkatan=form.cleaned_data['angkatan']
            )

            Membership.objects.create(
                user=user,
                role=Role.objects.get(name='Anggota'),
                unit=OrganizationUnit.objects.get(name='Organisasi Utama')
            )

            login(request, user)
            return redirect('dashboard')

    else:
        form = SignupForm()

    return render(
        request,
        'authentication/sign-up.html',
        {'form': form}
    )

def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 

    if request.method == 'POST':
        form = SigninForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('dashboard')
    else:
        form = SigninForm()

    return render(request, 'authentication/sign-in.html', {
        'form': form
    })

@login_required
def profile_view(request):
    user = request.user

    profile = getattr(user, 'profile', None)
    if profile is None:
        profile = MemberProfile(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = MemberProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.instance.user = user
            profile_form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = MemberProfileForm(instance=profile)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        request.user.foto_profil = request.FILES['avatar']
        request.user.save()
        messages.success(request, 'Foto profil berhasil diubah.')
    return redirect('profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password berhasil diubah.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect('profile')


@login_required
def detail_member(request, user_id):

    member = get_object_or_404(
        User.objects.select_related('profile'),
        pk=user_id
    )

    membership = Membership.objects.filter(
        user=member,
        is_active=True
    ).first()

    if request.method == "POST":

        user_form = MemberUserForm(
            request.POST,
            instance=member
        )

        profile_form = MemberProfileForm(
            request.POST,
            instance=member.profile
        )

        membership_form = MembershipForm(
            request.POST,
            instance=membership
        )

        if (
            user_form.is_valid()
            and profile_form.is_valid()
            and membership_form.is_valid()
        ):

            user_form.save()
            profile_form.save()
            membership_form.save()

            messages.success(
                request,
                "Data anggota berhasil diperbarui."
            )

            return redirect(
                'detail_member',
                user_id=member.id
            )

    else:

        user_form = MemberUserForm(
            instance=member
        )

        profile_form = MemberProfileForm(
            instance=member.profile
        )

        membership_form = MembershipForm(
            instance=membership
        )

    context = {
        'member': member,
        'membership': membership,

        'user_form': user_form,
        'profile_form': profile_form,
        'membership_form': membership_form,
    }

    return render(
        request,
        'organization/detail_user.html',
        context
    )