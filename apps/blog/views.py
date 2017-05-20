# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View

from .models import Blog
from .forms import AddBlogForm, BlogCommentForm
from courses.models import Forum
from utils.Redis import Redis


class BlogDetailView(View):
    """
    博客详情
    """
    def get(self, request, blog_id):
        # 手记实体
        blog = Blog.objects.get(id=blog_id)
        # 所有评论
        comments = blog.comments.all()
        form = BlogCommentForm()
        # 所有标签
        types = blog.type.all()
        # 记录用户操作
        r = Redis(request.user.username)
        for type in types:
            r.increase(type.name, 1)
        forum = blog.forum
        return render(request, 'forum-blog-detail.html', {'blog': blog,
                                                          'forum': forum,
                                                          'form': form,
                                                          'comments': comments})

    def post(self, request, blog_id):
        form = BlogCommentForm(request.POST)
        blog = Blog.objects.get(id=blog_id)
        comments = blog.comments.all()
        forum = blog.forum
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.author = request.user
            comment.save()
            return render(request, 'forum-blog-detail.html', {'blog': blog,
                                                              'form': form,
                                                              'comments': comments,
                                                              'forum': forum})

        return render(request, 'forum-blog-detail.html', {'blog': blog,
                                                          'form': form,
                                                          'comments': comments,
                                                          'forum': forum})


class AddBlogView(View):
    """
    添加手记
    """
    def get(self, request, forum_id):
        form = AddBlogForm()
        forum = Forum.objects.get(id=forum_id)
        return render(request, 'forum_blog_add.html', {'form': form,
                                                       'forum': forum})

    def post(self, request, forum_id):
        forum = Forum.objects.get(id=forum_id)
        form = AddBlogForm(request.POST)
        if form.is_valid():
            # 手记实体
            blog = form.save(commit=False)
            # 手记作者
            blog.author = request.user
            # 手记所在论坛
            blog.forum = forum
            blog.save()
            form.save_m2m()
            return render(request, 'forum-blog.html', {'forum': forum})

        return render(request, 'forum_blog_add.html', {'form': form,
                                                       'forum': forum})


class AddBlogCommentView(View):
    def post(self, request):
        pass


class DeleteBlogView(View):
    def get(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        return render(request, 'forum_delete_blog.html', {'blog': blog})

    def post(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        forum = blog.forum
        blogs = Blog.objects.filter(forum=forum)
        # 如果不是教师的话，则只能看到已发布的文章
        if not request.user.is_teacher:
            blogs = blogs.filter(status='published')
        if blog_id:
            if blog.status == 'draft':
                blog.status = 'published'
                blog.save()
                return render(request, 'forum-blog.html', {'blogs': blogs,
                                                           'forum': forum})
            if blog.status == 'published':
                blog.status = 'draft'
                blog.save()
                return render(request, 'forum-blog.html', {'blogs': blogs,
                                                           'forum': forum})
