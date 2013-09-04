from django import forms
from django.core.exceptions import ValidationError

from captain.projects.models import ScheduledCommand


class RunCommandForm(forms.Form):
    command = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_command(self):
        if self.cleaned_data['command'].strip() == '':
            raise ValidationError('Command cannot be blank.')
        return self.cleaned_data['command']


class CreateScheduledCommandForm(forms.ModelForm):
    class Meta:
        model = ScheduledCommand
        fields = ('command', 'interval_minutes')
        widgets = {
            'command': forms.TextInput(attrs={'class': 'form-control'}),
            'interval_minutes': forms.Select(attrs={'class': 'form-control'}),
        }
