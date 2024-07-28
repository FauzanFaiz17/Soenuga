from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

import requests
from django.shortcuts import render

def items_view(request):
    response = requests.get('http://localhost:8000/api/items/')
    items = response.json()
    return render(request, 'items.html', {'items': items})
