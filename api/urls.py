from django.conf.urls import url

from . import zone, record

urlpatterns = [
    url(r'^zone/([\w\-.]*)$', zone.ZoneView.as_view()),
    url(r'^record/([\w\-.]*)/([\w\-.@]*)$', record.RecordView.as_view())
]
