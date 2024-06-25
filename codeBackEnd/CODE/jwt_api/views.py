from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse
reference = apps.get_app_config("jwt_api").my_object
# Create your views here.
def get_keys(request):
    tooken, expdate = reference.TokenManager.make_configured_token("amine", "meftah", {"username":"meftah"})
    return JsonResponse({"JWT":tooken, "epired_date":expdate})


def get_dec(request):
    token = request.META.get('HTTP_AUTHORIZATION', '')
    print(token)
    try:
        token = token.replace("\\", "")
        decrepted = reference.decr_token(token)
        print("recieved", decrepted)
        return JsonResponse({"ok":decrepted.claims})
    except Exception as e:
        print(e)
        return JsonResponse({"ok":False})
    return JsonResponse({"ok":False})