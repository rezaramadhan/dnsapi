from django.conf.urls import url

from . import zone, record

urlpatterns = [
    url(r'^([\w.]*)$', zone.ZoneView.as_view()),
    url(r'^([\w.]*)/([\w.]*)$', record.RecordView.as_view())
]
