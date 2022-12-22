from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("create/", views.CreatePostFormView.as_view(), name="create_post"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post"),
    path("<int:pk>/comment", views.CommentFormHandlerView.as_view(), name="comment_post"),
]
