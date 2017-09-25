from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from . import views


app_name = 'reservierung'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'reservierung/form/$', views.reservierung_form, name='form'),
    url(r'reservierung/update/(?P<pk>[0-9]+)/$',
        views.ReservierungUpdate.as_view(), name='reservierung-update'),
    url(r'reservierung/(?P<pk>[0-9]+)/$',
        views.ReservierungDetail.as_view(), name='reservierung-detail'),
    url(r'reservierung/(?P<pk>[0-9]+)/delete/$',
        views.ReservierungDelete.as_view(), name='delete'),
    url(r'reservierung/$', views.ReservierungList.as_view(),
        name='reservierung-list'),
    url(r'reservierung/user/$', views.reservierung_user, name="user"),
]
