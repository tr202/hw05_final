from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('follow/', views.FollowIndex.as_view(), name='follow_index'),
    path('profile/<str:username>/follow/',
         views.FollowView.as_view(), name='profile_follow'),
    path('profile/<str:username>/unfollow/',
         views.UnfollowView.as_view(), name='profile_unfollow'),
    path('posts/<pk>/comment/',
         views.PostDetailWithCommentFormView.as_view(), name='add_comment'),
    path('posts/<pk>/',
         views.PostDetailWithCommentFormView.as_view(), name='post_detail'),
    path('create/', views.PostCreate.as_view(), name='post_create'),
    path('group/<str:slug>/', views.GroupPosts.as_view(), name='group_list'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path('posts/<pk>/edit/', views.PostEdit.as_view(), name='post_edit'),
    path('', views.IndexView.as_view(), name='index'),
]
