from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostListView(ListView):
    template_name = "blog/list_posts.html"
    context_object_name = 'posts'
    model = Post

    def get_queryset(self):
        order_by = self.request.GET.get("order_dy")
        search_str = self.request.GET.get("search")

        if order_by == "date":
            return Post.objects.filter(hide=False).order_by("-pub_date")
        elif order_by == "num_views":
            return Post.objects.filter(hide=False).order_by("-num_views")
        elif search_str:
            return Post.objects.filter(hide=False).filter(
                title__icontains=search_str)
        return Post.objects.filter(hide=False)


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(post=context["post"]).order_by(
            'pub_date')
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form = CommentForm()
        context["page_obj"] = page_obj
        context["form"] = form

        return context


class CommentFormHandlerView(View):
    form_class = CommentForm

    def get(self, request, pk):
        return HttpResponseRedirect(reverse("post", args=(pk,)))

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            post_obj = Post.objects.get(pk=pk)
            comment = Comment(post=post_obj, text=form.cleaned_data["text"])
            comment.save()
            return HttpResponseRedirect(reverse("post", args=(pk,)))


class CreatePostFormView(View):
    form_class = PostForm
    template_name = "blog/create_post.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            blog_post = Post(title=form.cleaned_data["title"],
                             text=form.cleaned_data["text"],
                             pub_date=timezone.now())
            blog_post.save()
            return HttpResponseRedirect(reverse("post", args=(blog_post.id,)))

        return render(request, self.template_name, {form: form})
