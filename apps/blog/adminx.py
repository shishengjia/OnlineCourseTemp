# -*- encoding: utf-8 -*-
import xadmin

from .models import Blog, BlogComment


class BlogAdmin(object):
    list_display = ['title', 'author', 'status', 'body']
    list_filter = ['status', 'author']


class BlogCommentAdmin(object):
    list_display = ['author', 'body', 'blog']
    list_filter = ['author']


xadmin.site.register(Blog, BlogAdmin)
xadmin.site.register(BlogComment, BlogCommentAdmin)