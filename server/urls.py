from django.urls import path
from . import views

app_name = "server"

urlpatterns = [
    path("infer_mask/", views.infer_mask, name="infer_mask"),
    path("infer_class/", views.infer_class, name="infer_class"),
    path("handle_image/", views.handle_image, name="handle_image"),
    path("score/", views.score, name="score")
]