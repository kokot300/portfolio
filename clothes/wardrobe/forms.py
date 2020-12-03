from django.contrib.auth.models import User
from django.forms import ModelForm, PasswordInput


class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        widgets = {'password': PasswordInput(attrs={'autocomplete': "new-password", }), }
