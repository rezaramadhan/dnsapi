# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from settings import TEMPLATES


def index(request):
    return render(request, 'index.html')

def network(request):
    return render(request, 'network.html')

def zones(request, zones_id):
    return render(request, 'zones-manage.html', {
                'zones_id': zones_id,
            })
