from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, EditUserForm, EditUserProfileForm
from .models import UserProfile
from django.contrib import messages
# Create your views here.

def login_view(request):
    logout(request)
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('metodo:home')
        else:
            return render(request, 'auth/login.html', {'form': form, 'error': 'Credenciales incorrectas'})
    else:
        form = AuthenticationForm()
    logout(request)
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def inicio_view(request):
    return render(request, 'inicio.html')

def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():  # Solo continúa si todo es válido
            # Guardar el usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'].lower(),
                password=form.cleaned_data['password1']
            )

            # Guardar el perfil adicional
            profile_data = {
                'user': user,
                'full_name': form.cleaned_data['full_name'].title().replace('  ', ' '),
            }

            UserProfile.objects.create(**profile_data)

            return redirect('login')  # Redirigir después del registro

    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

def edit_profile_view(request):
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditUserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('profile')  # O redirige donde desees
    else:
        user_form = EditUserForm(instance=user)
        profile_form = EditUserProfileForm(instance=profile)

    context = {
        'user': request.user,
        'profile': request.user.userprofile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profiles/profile.html', context)

def documentacion(request):
    return render(request, 'documentacion.html')

def creditos(request):
    return render(request,  'creditos.html')