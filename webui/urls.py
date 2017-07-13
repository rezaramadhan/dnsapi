from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^network$', views.network, name='network'),
    url(r'^network/zones$', views.zones, name='zones'),
]
