from django import forms
from .models import Event, EventParticipant, ActivityParticipant
from django.contrib.auth.models import Group


# CSS Class untuk styling form
INPUT_CLASS = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'


class EventForm(forms.ModelForm):
    """Form untuk membuat atau edit Event (Acara/Kegiatan)"""
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'tipe', 'start_date', 'end_date', 'lokasi', 'gdrive_link', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set widget untuk DateTimeInput
        datetime_fields = ['start_date', 'end_date']
        
        for field_name, field in self.fields.items():
            if field_name in datetime_fields:
                field.widget = forms.DateTimeInput(attrs={
                    'type': 'datetime-local',
                    'class': INPUT_CLASS,
                })
            else:
                field.widget.attrs.update({
                    'class': INPUT_CLASS,
                    'placeholder': field.label,
                })


class EventParticipantForm(forms.ModelForm):
    """Form untuk menambah peserta/panitia pada Event (Acara)"""
    
    class Meta:
        model = EventParticipant
        fields = ['user', 'role', 'is_active']
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs.update({
                    'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-700 dark:bg-gray-600 dark:border-gray-500',
                })
            else:
                field.widget.attrs.update({
                    'class': INPUT_CLASS,
                })
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validasi jika event sudah ada peserta dengan user yang sama
        if self.event and cleaned_data.get('user'):
            if EventParticipant.objects.filter(
                event=self.event,
                user=cleaned_data['user']
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    f"User {cleaned_data['user']} sudah menjadi peserta di event ini."
                )
        
        return cleaned_data


class ActivityParticipantForm(forms.ModelForm):
    """Form untuk menambah peserta pada Activity (Kegiatan)"""
    
    class Meta:
        model = ActivityParticipant
        fields = ['user', 'unit', 'status']
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': INPUT_CLASS,
            })
            
            # Set required untuk user dan unit menjadi tidak required (validasi di clean)
            if field_name in ['user', 'unit']:
                field.required = False
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        unit = cleaned_data.get('unit')
        
        # Validasi: minimal harus ada user atau unit
        if not user and not unit:
            raise forms.ValidationError(
                "Peserta harus berupa User atau Unit, tidak boleh kosong keduanya."
            )
        
        # Validasi: tidak boleh keduanya ada
        if user and unit:
            raise forms.ValidationError(
                "Peserta hanya bisa berupa User ATAU Unit, tidak boleh keduanya."
            )
        
        # Validasi jika event ada dan user sudah terdaftar
        if self.event and user:
            if ActivityParticipant.objects.filter(
                event=self.event,
                user=user
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    f"User {user} sudah menjadi peserta di event ini."
                )
        
        return cleaned_data
