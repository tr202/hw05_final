import logging
from functools import wraps

from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def is_post_author(view):
    @wraps(view)
    def wrap(request, post_id, *args, **kwargs):
        if request.user == Post.objects.get(pk=post_id).author:
            return view(request, post_id, *args, **kwargs)
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=(post_id,))
        )
    return wrap


@login_required
@is_post_author
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    context = {'form': form, 'is_edit': False, }
    return render(request, 'posts/create_post.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm()
    comments_list = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments_list,
    }
    return render(request, 'posts/post_detail.html', context)


@cache_page(settings.INDEX_PAGE_CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__in=request.user.follower.all())
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page_obj': page_obj, })


@login_required
def profile_follow(request, username):
    try:
        Follow.objects.create(
            author=User.objects.get(username=username), user=request.user)
    except IntegrityError as e:
        logging.exception(e)
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        author=User.objects.get(username=username), user=request.user).delete()
    return redirect('posts:profile', username=username)
