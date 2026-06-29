from django import forms
from .models import FeePeriod, Payment, FeeType, FinancialTransaction

INPUT_CLASS = (
    "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
    "focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
    "dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
)
SELECT_CLASS = (
    "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
    "focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 "
    "dark:bg-gray-700 dark:border-gray-600 dark:text-white "
    "dark:focus:ring-primary-500 dark:focus:border-primary-500"
)
TEXTAREA_CLASS = (
    "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border "
    "border-gray-300 focus:ring-primary-500 focus:border-primary-500 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
    "dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
)

# Input angka tanpa constraint browser (validasi di view)
NUMBER_CLASS = (
    "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg "
    "focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
    "dark:text-white"
)


def apply_widget_classes(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.Select):
            widget.attrs.update({'class': SELECT_CLASS})
        elif isinstance(widget, forms.Textarea):
            widget.attrs.update({'class': TEXTAREA_CLASS, 'rows': 3})
        else:
            widget.attrs.update({'class': INPUT_CLASS})


# ── Buat Periode Kas / Iuran ──────────────────────────────────
class FeePeriodForm(forms.ModelForm):
    class Meta:
        model   = FeePeriod
        fields  = ['fee_type', 'title', 'amount', 'due_date', 'description']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}
        labels  = {
            'fee_type':    'Jenis Iuran',
            'title':       'Judul / Label Periode',
            'amount':      'Nominal (Rp)',
            'due_date':    'Batas Waktu Bayar',
            'description': 'Keterangan (opsional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fee_type'].queryset = FeeType.objects.filter(is_active=True)
        apply_widget_classes(self)


# ── Buat Transaksi Manual (pemasukan / pengeluaran) ───────────
class ManualTransactionForm(forms.ModelForm):
    class Meta:
        model   = FinancialTransaction
        fields  = ['transaction_type', 'transaction_date', 'amount', 'description']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels  = {
            'transaction_type': 'Jenis Transaksi',
            'transaction_date': 'Tanggal',
            'amount':           'Jumlah (Rp)',
            'description':      'Keterangan',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_widget_classes(self)


# ── Catat Pembayaran Tagihan Kas / Iuran ─────────────────────
class PaymentForm(forms.ModelForm):
    class Meta:
        model  = Payment
        fields = ['amount', 'notes']
        labels = {'amount': 'Jumlah Dibayar (Rp)', 'notes': 'Catatan'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_widget_classes(self)


# ── Form konfirmasi bayar denda ───────────────────────────────
# Sengaja pakai CharField bukan DecimalField agar tidak ada
# constraint otomatis dari browser (max_digits dll). Konversi
# ke Decimal dilakukan di view dengan validasi manual.
class ActivityFinePayForm(forms.Form):
    amount = forms.CharField(
        label='Jumlah Dibayar (Rp)',
        widget=forms.TextInput(attrs={
            'class': NUMBER_CLASS,
            'inputmode': 'numeric',
            'placeholder': 'Contoh: 5000',
        }),
    )
    notes = forms.CharField(
        required=False,
        label='Catatan',
        widget=forms.Textarea(attrs={
            'class': TEXTAREA_CLASS,
            'rows': 2,
        }),
    )
