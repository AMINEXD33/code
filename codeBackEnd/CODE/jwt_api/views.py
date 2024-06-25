from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
reference = apps.get_app_config("jwt_api").my_object
# Create your views here.
@require_http_methods(["GET"])
@csrf_exempt
def get_keys(request):
    tooken, expdate = reference.TokenManager.make_configured_token("amine", "meftah", {"username":"meftah"})
    return JsonResponse({"JWT":tooken, "expired_date":expdate})

@require_http_methods(["POST"])
@csrf_exempt
def get_dec(request):
    json_token = request.META.get('HTTP_AUTHORIZATION', '')
    obj_token = None
    body = None

    # try and get the token and the username and password
    try:
        obj_token = json.loads(json_token)
        print(obj_token)
    except Exception as e:
        print(e)
        return JsonResponse({"error parsing token":True})

    try:
        body = request.body.decode('utf-8')
        body = json.loads(body)
    except Exception as e:
        print(e)
        return JsonResponse({"error parsing body":True})

    if not body["username"] or not body["password"]:
         return JsonResponse({"autherror":False})
    reference.TokenManager.abstract_token_validation(body["username"], body["password"], obj_token["JWT"], obj_token["expired_date"])
    # print(token)
    # try:
    #     token = token.replace("\\", "")
    #     decrepted = reference.decr_token(token)
    #     print("recieved", decrepted)
    #     return JsonResponse({"ok":decrepted.claims})
    # except Exception as e:
    #     print(e)
    #     return JsonResponse({"ok":False})
    return JsonResponse({"ok":False})