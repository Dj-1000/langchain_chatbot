from django.shortcuts import render
from django.contrib import auth
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render,redirect
from .forms import CreateUserForm,LoginForm
from django.urls import reverse
from django.contrib import messages
from chat.models import Room

User = get_user_model()

def register(request):
    form = CreateUserForm()
    if request.method=='POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect(reverse('login'))
        else:
            messages.error(request, 'There was an error with your registration. Please try again.')
    
    return render(request,'register.html', {'form': form})


def login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=email, password=password)
            print("USER : ", user)
            if user is not None:
                auth.login(request, user)
                room = Room()
                room.save()
                return redirect(reverse('chat_view',kwargs={"room_id" : room.id}))

            else:
                messages.error(request, 'Invalid username or password')
                        
    return render(request, "login.html", context={"form": form})


def logout(request):
    auth.logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    user = User.objects.get(id = request.user.id)
    if user:
        print("User :",user)
        users = User.objects.exclude(username = user)
        return render(request,'dashboard.html',{'users':users})
    






