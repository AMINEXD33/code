from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer
from django.apps import apps


from django.shortcuts import render

# Create your views here.
def get_keys():
    reference = apps.get_app_config("JWT_api").my_object
    
