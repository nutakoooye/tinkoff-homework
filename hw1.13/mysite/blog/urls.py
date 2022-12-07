from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_post, name="create_post"),
    path("<int:post_id>/", views.post_detail, name="post"),
    path("<int:post_id>/comment", views.comment_post, name="comment_post"),
]
