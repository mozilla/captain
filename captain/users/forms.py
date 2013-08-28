from django import forms

from captain.users.models import UserProfile


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'})
        }
