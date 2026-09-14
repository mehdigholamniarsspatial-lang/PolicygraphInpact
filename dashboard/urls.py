from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.index, name="index"),
    path("api/dataset/", views.dataset, name="dataset"),
    path("api/validate/", views.validate_upload, name="validate-upload"),
    path("health/", views.health, name="health"),
]
