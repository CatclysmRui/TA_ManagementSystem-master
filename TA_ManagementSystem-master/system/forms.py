from django import forms
from django.forms import modelform_factory
from .models import TADuty, TA


class DutyCreateForm(forms.ModelForm):
    class Meta:
        model = TADuty
        fields = ('labNumber', 'preparationHour', 'labHour', 'labWorkingHour', 'assignmentNumber',
                  'assignmentWorkingHour', 'contactHour', 'otherDutiesHour')

