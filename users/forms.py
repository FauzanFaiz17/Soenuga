from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from organization.models import MemberProfile, ProgramStudi
from django.contrib.auth import get_user_model



User = get_user_model()

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
    program_studi = forms.ModelChoiceField(
        queryset=ProgramStudi.objects.all(),
        required=True
    )
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
            'program_studi',
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

            