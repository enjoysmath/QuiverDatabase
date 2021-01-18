from django.shortcuts import render

# Create your views here.

# views.py
from django.shortcuts import render, redirect
from .forms import SignUpForm


# Create your views here.
def user_signup(response):
    if response.method == "POST":
        form = SignUpForm(response.POST)
        if form.is_valid():
            form.save()

        return redirect("home")
    else:
        form = SignUpForm()

    return render(response, "signup.html", {"form": form})