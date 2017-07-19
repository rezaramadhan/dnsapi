from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^network/$', views.network, name='network'),
    url(r'^network/([\w\-.]*)/$$', views.zones, name='zones'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/$$', views.zones_manage, name='zones_manage'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/([\w\-.@]*)/$$', views.records_manage, name='records_manage'),
    url(r'^network/([\w\-.]*)/([\w\-.]*)/([\w\-.@]*)/([\w\-.@]*)/$$', views.records_action, name='records_action'),
    url(r'^debug$', views.debug, name='debug'),
]
