from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ParticipationRequest
from .models import Activity 

class ParticipationRequestForm(forms.ModelForm):
    class Meta:
        model = ParticipationRequest
        fields = ['first_name', 'last_name', 'room_number', 'email', 'phone', 'special_needs']
        labels = {
            'first_name': _('Fornavn'),
            'last_name': _('Etternavn'),
            'room_number': _('Romnummer'),
            'email': _('E-post'),
            'phone': _('Telefonnummer'),
            'special_needs': _('Spesielle behov'),
        }
        