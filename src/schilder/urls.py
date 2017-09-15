from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'schilder'

urlpatterns = [
    url(r'schilder/$', views.SchilderList.as_view(), name="schilder-list"),
    url(r'schilder/(?P<pk>[0-9]+)/$', views.schilder_detail, name="schilder-detail"),
    url(r'schilder/(?P<pk>[0-9]+)/reservierung_form/$',
     views.reservierung_form, name="reservierung"),
    url(r'schilder/reservierung_detail/(?P<pk>[0-9]+)/$',
     views.SchilderReservierungDetail.as_view(), name='reserv-detail'),
    url(r'schilder/(?P<room>[0-9]+)/login/$', views.schilder_login, name='login'),
    url(r'schilder/(?P<room>[0-9]+)/logout/$', views.schilder_logout, name='logout'),
]
