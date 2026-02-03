from django import forms

class RoleForm(forms.Form):
    name = forms.CharField(
        label="Nama Role",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full p-2.5 text-sm rounded-lg border border-gray-300 dark:bg-gray-700 dark:text-white"
        })
    )

    is_leader = forms.BooleanField(
        label="Role Pimpinan",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "w-4 h-4 text-blue-600 rounded border-gray-300"
        })
    )
