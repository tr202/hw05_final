import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView, )

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


class PostEdit(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        post = super().get_object()
        is_author = self.request.user == post.author
        if is_author:
            return super(PostEdit, self).dispatch(request, *args, **kwargs)
        return redirect(reverse('posts:post_detail', kwargs={
            'pk': post.pk
        }))

    def get_context_data(self, **kwargs):
        post = super().get_object()
        is_author = self.request.user == post.author
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit'
        context['is_edit'] = is_author
        return context

    def form_valid(self, form):
        if self.request.user == super().get_object().author:
            form.save()
        return redirect(reverse('posts:post_detail', kwargs={
            'pk': form.instance.pk
        }))


class PostCreate(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect(reverse('posts:profile', kwargs={
            'username': form.instance.author.username
        }))


class PostCommentCreate(LoginRequiredMixin, CreateView):
    template_name = 'posts/post_detail.html'
    model = Post
    form_class = CommentForm

    def form_valid(self, form, **kwargs):
        form.instance.author = self.request.user
        post = self.get_object()
        form.instance.post = post
        form.save()
        return redirect(reverse('posts:post_detail', kwargs={
            'pk': form.instance.post.pk
        }))


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        post = super().get_object()
        context['comments'] = post.comments.all()
        return context


class PostDetailWithCommentFormView(View):

    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostCommentCreate.as_view()
        return view(request, *args, **kwargs)


def paginate(self, obj_list, count=settings.PAGE_POSTS_COUNT):
    paginator = Paginator(obj_list, count)
    page_number = self.request.GET.get('page')
    return paginator.get_page(page_number)


class IndexView(ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'page_obj'

    def get_context_data(self):
        posts = cache.get('posts')
        if not posts:
            posts = Post.objects.all()
            cache.set('posts', posts, 20)
        page_obj = paginate(self, posts)
        return {'page_obj': page_obj, }


class GroupPosts(ListView):
    model = Post
    template_name = 'posts/group_list.html'
    context_object_name = 'page_obj'

    def get_context_data(self, *args, **kwargs):
        ctx = super(GroupPosts, self).get_context_data(*args, **kwargs)
        ctx['slug'] = self.kwargs['slug']
        group = get_object_or_404(Group, slug=ctx['slug'])
        post_list = group.posts.all()
        page_obj = paginate(self, post_list)
        return {'page_obj': page_obj, 'group': group}


class Profile(ListView):
    model = Post
    template_name = 'posts/profile.html'
    context_object_name = 'page_obj'

    def get_context_data(self, *args, **kwargs):
        ctx = super(Profile, self).get_context_data(*args, **kwargs)
        ctx['username'] = self.kwargs['username']
        author = get_object_or_404(User, username=ctx['username'])
        following = False
        if self.request.user.is_authenticated:
            following = author.following.filter(
                user=self.request.user).exists()
        post_list = author.posts.all()
        count = post_list.count()
        page_obj = paginate(self, post_list)
        return {
            'page_obj': page_obj,
            'author': author,
            'following': following,
            'count': count}


class FollowIndex(LoginRequiredMixin, ListView):
    template_name = 'posts/follow.html'
    model = Post
    context_object_name = 'page_obj'

    def get(self, *args, **kwargs):
        post_list = Post.objects.filter(
            author__following__in=self.request.user.follower.all())
        paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(
            self.request, 'posts/follow.html', {'page_obj': page_obj, })


class FollowView(LoginRequiredMixin, CreateView):
    model = User

    def get(self, request, username, *args, **kwargs):
        try:
            Follow.objects.create(
                author=User.objects.get(username=username), user=request.user)
        except IntegrityError as e:
            logging.exception(e)
        return redirect('posts:profile', username=username)


class UnfollowView(LoginRequiredMixin, DeleteView):
    model = User

    def get(self, request, username):
        Follow.objects.filter(
            author=User.objects.get(
                username=username), user=request.user).delete()
        return redirect('posts:profile', username=username)
