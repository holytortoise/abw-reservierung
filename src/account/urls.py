from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'

urlpatterns = [
    # Predefined Views
    url(r'login/$', auth_views.LoginView.as_view(template_name="account/login.html"), name='login'),
    url(r'logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url('^password_change/done/$',
     auth_views.PasswordChangeDoneView.as_view(template_name="account/password_change_done.html"),
      name='password-change-done'),
    url('^password_change/$',
     auth_views.PasswordChangeView.as_view(template_name="account/password_change.html"), name='password-change'),

]
