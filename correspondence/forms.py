from django import forms
from .models import Correspondence


class CorrespondenceForm(forms.ModelForm):
    class Meta:
        model = Correspondence
        fields = ['nomor', 'perihal', 'jenis', 'tanggal', 'keterangan', 'pengirim', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_classes = (
            'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg '
            'focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 '
            'dark:border-gray-600 dark:placeholder-gray-400 dark:text-white'
        )

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': base_classes,
                'placeholder': field.label,
                'required': False,
            })

        # Khusus field `tanggal`, ganti ke input type="date"
        self.fields['tanggal'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': base_classes,
        })

        # Khusus file, pastikan class tambahan seperti di contohmu
        self.fields['file'].widget.attrs.update({
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer '
                     'bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 '
                     'dark:border-gray-600 dark:placeholder-gray-400',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
        })
