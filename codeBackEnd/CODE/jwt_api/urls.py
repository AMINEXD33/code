
from django.urls import path
from jwt_api import views
urlpatterns = [
    path('keys/', views.get_keys),
    path('dec/', views.get_dec)
]
