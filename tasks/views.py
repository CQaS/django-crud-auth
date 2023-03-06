from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:

                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('tasks')

            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'err': 'Usuario ya existe!'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'err': 'Password no iguales'
        })

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })

    else:
        us = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if us is None:

            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'err': 'Usuario o password incorrectos'
            })

        else:
            login(request, us)
            return redirect('tasks')

@login_required
def task_detalle(request, task_id):

    t = get_object_or_404(Task, pk=task_id,user = request.user)

    if request.method == 'GET':        
        form = TaskForm(instance = t)
        return render(request, 'task_detalle.html', {'task': t,'form':form})
        
    else:
        try:
            form = TaskForm(request.POST, instance=t)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detalle.html', {'task' : t,'form' : form, 'err' : 'No se pudo Actualizar'})

@login_required
def delete_task(request, task_id):
   t = get_object_or_404(Task, pk=task_id, user=request.user)
   if request.method == 'POST':
       t.delete()
       return redirect('tasks')

@login_required
def completa_task(request, task_id):
   t = get_object_or_404(Task, pk=task_id, user=request.user)
   if request.method == 'POST':
       t.completo = timezone.now()
       t.save()
       return redirect('tasks')

@login_required
def tasks(request):
    t = Task.objects.filter(user=request.user, completo__isnull=True)
    return render(request, 'tasks.html', {'tasks': t})

@login_required
def tasks_completas(request):
    t = Task.objects.filter(user=request.user, completo__isnull=False).order_by('-completo')
    return render(request, 'tasks.html', {'tasks': t})

@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })

    else:
        try:
            form = TaskForm(request.POST)
            n_t = form.save(commit=False)
            n_t.user = request.user
            n_t.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'err': 'ERROR:IngresaDatosValidos'
            })

def cerrar(request):
    logout(request)
    return redirect('home')
