import tempfile

from django.conf import settings as s
from django.core.files.uploadedfile import SimpleUploadedFile

APP_NAME = 'posts'

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)

OBJECT_RELATED_URL_PARAMS = {
    # name_url:(object:orm_name)
    'slug': ('group', 'slug',),
    'pk': ('post', 'pk',),
    'username': ('user', 'username',),
}

CONFIG_TEST_URLS = {
    # name : [url{param}, template, redirect_url]
    'follow_index': ['/follow/', 'posts/follow.html'],
    'index': ['/', 'posts/index.html'],
    'group_list': ['/group/{slug}/', 'posts/group_list.html'],
    'profile': ['/profile/{username}/', 'posts/profile.html'],
    'post_create': ['/create/', 'posts/create_post.html', '/auth/login/'],
    'post_detail': ['/posts/{pk}/', 'posts/post_detail.html'],
    'post_edit': [
        '/posts/{pk}/edit/', 'posts/create_post.html',
        '/posts/{pk}/'],
}
COMMENTS_URL = 'comment/'
COMMENTS_UNAUTHORIZED_REDIRECT = '/auth/login/'
PAGINATOR_TEST_PAGES = ('group_list', 'profile', 'index',)
UNEXISTING_URL = '/unexisting/'
AUTHORISATION_PAGES_CASES = ('post_create', 'post_edit',)
POST_APPEAR_ON_PAGES = ('group_list', 'profile', 'index',)
PAGE_SHOW_CORRECT_CONTEXT = ('group_list', 'profile', 'index',)
PAGES_USES_CREATE_TEMPLATE = ('post_create', 'post_edit',)
PAGES_SHOW_SINGLE_POST = ('post_detail',)
INDEX_PAGE = ('/')
FOLLOW_UNFOLLOW = {
    'follow': 'posts:profile_follow', 'unfollow': 'posts:profile_unfollow'}
FOLLOWED_AUTHORS_TAPE = 'posts:follow_index'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=s.BASE_DIR)
