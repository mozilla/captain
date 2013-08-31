from django import forms
from django.core.exceptions import ValidationError


class RunCommandForm(forms.Form):
    command = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_command(self):
        if self.cleaned_data['command'].strip() == '':
            raise ValidationError('Command cannot be blank.')
        return self.cleaned_data['command']
