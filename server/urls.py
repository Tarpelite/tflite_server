from django.urls import path
from . import views

app_name = "server"

urlpatterns = [
    path("infer/", views.infer, name="infer"),
]