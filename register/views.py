from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserCreationForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth.views import  PasswordResetCompleteView,PasswordResetDoneView
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. You are now logged in.')
        login(request,user)
        return redirect('/')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('/')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your ToDoHex account'
    message = render_to_string('email_activate_account.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"
    if email.send():
        messages.success(request, f'Activation link sent to <b>{to_email}</b>')
    else:
        messages.error(request, f'There was a problem sending confirmation email to {to_email}, please confirm email is correct.')

def deleteEmail(to_email):
    mail_subject = 'Your ToDoHex account has been deleted'
    email = EmailMessage(mail_subject, 'Sorry to see you go. Your ToDoHex account has been deleted.', to=[to_email])
    email.content_subtype = "html"
    email.send()

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request,user,form.cleaned_data.get('email'))
            return redirect('/')
        else:
            for error in (form.errors.values()):
                messages.error(request,error)
            
    else:
        form = UserCreationForm()

    return render(request, "register/register.html", {"form":form})

@login_required(login_url='/login/')
def account_settings(request):
    if request.method == "POST":
        user = request.user
        email = user.email
        user.delete()
        deleteEmail(email)
        messages.success(request, f"ToDoHex account <b>{email}</b> was deleted")
        return redirect("/")
            
    return render(request, "account_settings.html", {})

class PasswordResetCompleteView(PasswordResetCompleteView):
    def dispatch(self, *args, **kwargs):
        super().dispatch(*args, **kwargs)
        messages.success(self.request,'Your password has been reset successfully. You may sign in now.')
        return redirect('login')
    
class PasswordResetDoneView(PasswordResetDoneView):
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        message = render_to_string('registration/password_reset_sent.html')
        messages.success(self.request,message)
        return redirect('password_reset')