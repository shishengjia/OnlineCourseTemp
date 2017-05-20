# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import BlogDetailView, AddBlogView, AddBlogCommentView, DeleteBlogView
_author_ = 'shishengjia'
_date_ = '13/01/2017 16:17'


urlpatterns = [
    url(r'^(?P<blog_id>\d+)/$', BlogDetailView.as_view(), name="blog_detail"),
    url(r'^add_blog/(?P<forum_id>\d+)/$', AddBlogView.as_view(), name="blog_add"),
    url(r'^add_comment/$', AddBlogCommentView.as_view(), name="blog_add_blog_comment"),
    url(r'delete_blog/(?P<blog_id>\d+)/$', DeleteBlogView.as_view(), name='delete_blog')
]
