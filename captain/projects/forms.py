from django import forms
from django.core.exceptions import ValidationError

from captain.projects.models import ScheduledCommand, ShoveInstance


class RunCommandForm(forms.Form):
    command = forms.CharField(required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    shove_instances = forms.ModelMultipleChoiceField(
        required=True, queryset=ShoveInstance.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        # Set queryset for shove_instances field to instances from the
        # given project.
        project = kwargs.pop('project')
        super(RunCommandForm, self).__init__(*args, **kwargs)

        self.fields['shove_instances'].queryset = project.shove_instances.filter(active=True)

    def clean_command(self):
        if self.cleaned_data['command'].strip() == '':
            raise ValidationError('Command cannot be blank.')
        return self.cleaned_data['command']


class CreateScheduledCommandForm(forms.ModelForm):
    hostnames = forms.ModelMultipleChoiceField(
        required=True, queryset=ShoveInstance.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        # Set queryset for hostnames field to instances from the
        # given project.
        project = kwargs.pop('project')
        super(CreateScheduledCommandForm, self).__init__(*args, **kwargs)

        self.fields['hostnames'].queryset = project.shove_instances.filter(active=True)

    def clean_hostnames(self):
        """
        Convert list of models to comma-seperated hostnames that the
        model expects.
        """
        shove_instances = self.cleaned_data['hostnames']
        return ','.join([instance.hostname for instance in shove_instances])

    class Meta:
        model = ScheduledCommand
        fields = ('command', 'interval_minutes', 'hostnames')
        widgets = {
            'command': forms.TextInput(attrs={'class': 'form-control'}),
            'interval_minutes': forms.Select(attrs={'class': 'form-control'}),
        }
