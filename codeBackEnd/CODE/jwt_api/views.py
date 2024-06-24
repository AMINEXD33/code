from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
def get_keys(request):
    reference = apps.get_app_config("jwt_api").my_object
    
    token = reference.make_token(**{"amine":"meftah"})

    return JsonResponse({"token":token})