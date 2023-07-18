from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView

urlpatterns = [
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("register/",views.register, name = "register" ),
]