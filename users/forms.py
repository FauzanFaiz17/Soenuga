from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from organization.models import MemberProfile, ProgramStudi, Role, OrganizationUnit, Membership
from django.contrib.auth import get_user_model



User = get_user_model()


FORM_CLASS = (
    'shadow-sm bg-gray-50 border border-gray-300 '
    'text-gray-900 sm:text-sm rounded-lg '
    'focus:ring-primary-500 focus:border-primary-500 '
    'block w-full p-2.5 '
    'dark:bg-gray-700 dark:border-gray-600 '
    'dark:text-white'
)


class SigninForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True, 
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
        'placeholder': 'name@company.com'
    }))
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            'placeholder': '••••••••'
        }),
    )

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    npm = forms.CharField(max_length=20)

    angkatan = forms.CharField(
        max_length=2,
        help_text="Contoh: 21"
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'npm',
            'angkatan',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'placeholder': field.label,
                'class': (
                    'bg-gray-50 border border-gray-300 text-gray-900 '
                    'sm:text-sm rounded-lg focus:ring-primary-500 '
                    'focus:border-primary-500 block w-full p-2.5 '
                    'dark:bg-gray-700 dark:border-gray-600 '
                    'dark:placeholder-gray-400 dark:text-white '
                    'dark:focus:ring-primary-500 dark:focus:border-primary-500'
                )
            })


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'nomor_telepon',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg '
                         'focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'required': False
            })

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ('npm', 'program_studi', 'angkatan')

    def clean_angkatan(self):
        angkatan = self.cleaned_data.get('angkatan')
        if angkatan and (not angkatan.isdigit() or len(angkatan) != 2):
            raise forms.ValidationError("Angkatan harus 2 digit angka.")
        return angkatan

    def clean(self):
        cleaned = super().clean()

        if not self.instance.pk:
            if not all([
                cleaned.get('npm'),
                cleaned.get('angkatan'),
                cleaned.get('program_studi'),
            ]):
                raise forms.ValidationError(
                    "NPM, Program Studi, dan Angkatan wajib diisi."
                )

        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg '
                         'focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 '
                         'dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'required': False
            })

            


# untuk admin

class MemberUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'nomor_telepon',
            'is_active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': FORM_CLASS
            })

class MemberProfileForm(forms.ModelForm):

    class Meta:
        model = MemberProfile
        fields = (
            'npm',
            'angkatan',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': FORM_CLASS
            })

class MembershipForm(forms.ModelForm):

    role = forms.ModelChoiceField(
        queryset=Role.objects.order_by('name')
    )

    unit = forms.ModelChoiceField(
        queryset=OrganizationUnit.objects.order_by('name')
    )

    class Meta:
        model = Membership
        fields = (
            'role',
            'unit',
            'is_active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': FORM_CLASS
            })