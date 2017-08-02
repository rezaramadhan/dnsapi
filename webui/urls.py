from django.conf.urls import url

from . import views
from django.views.generic.base import RedirectView


favicon_view = RedirectView.as_view(url='/static/assets/images/favicon.ico', permanent=True)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^network/$', views.network, name='network'),
    url(r'^network/([\w\-.]*)/$$', views.zones, name='zones'),
    url(r'^network/([\w\-.]*)/add/$$', views.zones_add, name='zones_add'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/$$', views.zones_manage, name='zones_manage'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/([\w\-.@]*)/$$', views.records_manage, name='records_manage'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/([\w\-.@]*)/([\w\-.@]*)/$$', views.records_action, name='records_action'),
    url(r'^help/$', views.help, name='help'),
    url(r'^favicon\.ico$', favicon_view),
    url(r'^debug$', views.debug, name='debug'),
]
