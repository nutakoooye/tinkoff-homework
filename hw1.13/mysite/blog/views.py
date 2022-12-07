from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import  HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .models import Post, Comment


def index(request):
    order_by = request.GET.get("order_dy")
    search_str = request.GET.get("search")
    if order_by == "date":
        all_posts = Post.objects.filter(hide=False).order_by("-pub_date")
    elif order_by == "num_views":
        all_posts = Post.objects.filter(hide=False).order_by("-num_views")
    elif search_str:
        all_posts = Post.objects.filter(hide=False).filter(
            title__icontains=search_str)
    else:
        all_posts = Post.objects.filter(hide=False)

    return render(request, "blog/index.html", {"posts": all_posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    post.num_views += 1
    post.save()

    comments = Comment.objects.filter(post=post).order_by('pub_date')
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"post": post,
               "page_obj": page_obj}
    return render(request, "blog/post_detail.html", context)


def comment_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    comment_text = request.POST['comment'].strip()
    if len(comment_text) == 0:
        context = {'post': post,
                   'error_message': "You are trying to send an empty comment."}
        return render(request, 'blog/post_detail.html', context)
    else:
        comm = Comment(post=post, text=comment_text)
        comm.save()
        return HttpResponseRedirect(reverse("post", args=(post_id,)))


def create_post(request):
    if request.method == "GET":
        return render(request, 'blog/create_post.html')
    else:
        title = request.POST['title'].strip()
        text = request.POST['text'].strip()

        if 200 <= len(title) or len(title) <= 0 or len(text) <= 0:
            context = {'error_message': "All fields are not filled in \
                                         or the title is too long"}
            return render(request, 'blog/create_post.html', context)
        else:
            post = Post(title=title, text=text, pub_date=timezone.now())
            post.save()
            return HttpResponseRedirect(reverse("post", args=(post.id,)))
