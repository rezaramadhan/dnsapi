from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^network$', views.network, name='network'),
    url(r'^network/zones/([\w\-.]*)/$$', views.zones, name='zones'),
    url(r'^network/zones/([\w\-.]*)/([\w\-.@]*)/$$', views.records, name='records'),
    url(r'^network/zones/([\w\-.]*)/([\w\-.@]*)/([\w\-.@]*)/$$', views.records_action, name='records_action'),
    url(r'^debug$', views.debug, name='debug'),
]
