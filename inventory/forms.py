from django import forms
from .models import Inventory, FotoInventory
from django.forms.widgets import FileInput


# =========================
# Multi File Input
# =========================
class MultiFileInput(FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)

        if attrs is None:
            attrs = {}

        attrs['multiple'] = True
        self.attrs.update(attrs)


# =========================
# Inventory Form
# =========================
class InventoryForm(forms.ModelForm):

    class Meta:
        model = Inventory
        fields = [
            'nama',
            'tipe',
            'sebelum',
            'ditambah',
            'dipakai',
            'rusak',
            'habis',
            'tanggal',
            'keterangan',
        ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Styling semua field (tetap sama seperti sebelumnya)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': (
                    'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm '
                    'rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 '
                    'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                    'dark:text-white'
                ),
                'placeholder': field.label,
                'required': False,
            })

        # Khusus select (tipe barang) → biar konsisten style
        self.fields['tipe'].widget.attrs.update({
            'class': (
                'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm '
                'rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 '
                'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            )
        })

        # Custom Date Input (tetap sama)
        self.fields['tanggal'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': (
                    'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm '
                    'rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 '
                    'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 '
                    'dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
                ),
            }
        )


    # =========================
    # Validasi Pintar (Opsional tapi Disarankan)
    # =========================
    def clean(self):
        cleaned_data = super().clean()

        tipe = cleaned_data.get('tipe')

        dipakai = cleaned_data.get('dipakai') or 0
        rusak = cleaned_data.get('rusak') or 0
        habis = cleaned_data.get('habis') or 0

        # Kalau consumable → jangan isi dipakai & rusak
        if tipe == 'consumable':

            # reset otomatis (biar tidak error)
            cleaned_data['dipakai'] = 0
            cleaned_data['rusak'] = 0

            if habis <= 0:
                raise forms.ValidationError(
                    "Barang habis pakai wajib mengisi jumlah habis."
                )

        # Kalau asset → jangan isi habis
        elif tipe == 'asset':

            # reset otomatis
            cleaned_data['habis'] = 0

            if dipakai < 0 or rusak < 0:
                raise forms.ValidationError(
                    "Nilai tidak boleh negatif."
                )

        return cleaned_data


# =========================
# Multi Foto Form
# =========================
class MultiFotoForm(forms.Form):

    foto = forms.FileField(
        widget=MultiFileInput(attrs={
            'accept': 'image/*',
            'class': (
                'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg '
                'cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none '
                'dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            )
        }),
        required=False
    )
