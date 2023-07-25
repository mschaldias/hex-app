from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView

urlpatterns = [
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("register/",views.register, name = "register" ),
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset.html',email_template_name='registration/email_password_reset.html',subject_template_name="registration/email_password_reset_subject.txt"),name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_confirm.html'),name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path("account_settings/",views.account_settings, name = "account_settings" ),

]