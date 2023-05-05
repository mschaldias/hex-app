from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm


# Create your views here.
def register(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect("/")
    
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"form":form})