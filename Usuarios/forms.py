from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.translation import gettext_lazy as _
import re

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': _('La contraseña es obligatoria.')}
    )
    password2 = forms.CharField(
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': _('Por favor confirma tu contraseña.')}
    )

    full_name = forms.CharField(
        label=_('Nombre completo'),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': _('El nombre completo es obligatorio.')}
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _('Nombre de usuario'),
            'email': _('Correo electrónico'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
        }
        error_messages = {
            'username': {
                'required': _('El nombre de usuario es obligatorio.'),
                'unique': _('Este nombre de usuario ya está en uso.'),
            },
            'email': {
                'required': _('El correo electrónico es obligatorio.'),
                'invalid': _('Ingresa un correo electrónico válido.'),
                'unique': _('Este correo ya está registrado.'),
            }
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Las contraseñas no coinciden."))

        try:
            validate_password(password1)
        except ValidationError as e:
            raise forms.ValidationError([_("Contraseña inválida: ") + msg for msg in e.messages])

        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Este nombre de usuario ya está en uso."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Este correo ya está registrado."))
        return email

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _('Nombre de usuario'),
            'email': _('Correo electrónico'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. juan123', 'required': 'required'} ),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej. correo@ejemplo.com', 'required': 'required'}),
        }
        error_messages = {
            'username': {
                'required': _('El nombre de usuario es obligatorio.'),
                'max_length': _('El nombre de usuario es demasiado largo.'),
            },
            'email': {
                'required': _('El correo electrónico es obligatorio.'),
                'invalid': _('Por favor, introduce un correo válido.'),
            },
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError(_("El nombre de usuario solo puede contener letras, números y guiones bajos."))

        if len(username) < 4:
            raise forms.ValidationError(_("El nombre de usuario debe tener al menos 4 caracteres."))

        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Este nombre de usuario ya está en uso."))

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Este correo electrónico ya está registrado."))

        return email


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name']
        labels = {
            'full_name': _('Nombre completo'),
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'full_name': {
                'required': _('El nombre completo es obligatorio.'),
            },
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', full_name):
            raise forms.ValidationError(_("El nombre completo solo puede contener letras y espacios."))
        return full_name