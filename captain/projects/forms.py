from django import forms


class RunCommandForm(forms.Form):
    command = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
