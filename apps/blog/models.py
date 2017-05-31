# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone

from ckeditor.fields import RichTextField

from courses.models import Type, Forum
from users.models import UserProfile


class Blog(models.Model):
    """
    文章模型
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    title = models.CharField(max_length=250)
    type = models.ManyToManyField(Type, verbose_name=u"手记标签")
    author = models.ForeignKey(UserProfile, related_name='blog_posts', verbose_name=u"作者")
    forum = models.ForeignKey(Forum, verbose_name=u"所属论坛")
    body = RichTextField(blank=True, null=True, verbose_name=u"内容")
    publish_time = models.DateTimeField(default=timezone.now)
    # auto_now_add here, the date will be saved automatically when creating an object.
    created_time = models.DateTimeField(auto_now_add=True)
    # auto_now here, the date will be updated automatically when saving an object.
    updated_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')

    class Meta:
        # sort results by the publish_time field in descending order by default when we query the database.
        ordering = ('-publish_time', )
        verbose_name = u"文章"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.title

    def get_comment_nums(self):
        return self.comments.all().count()


class BlogComment(models.Model):
    """
    评论模型
    """
    # 定义related_name属性为comments，可以post.comments.all()访问文章的所有评论，默认是post.comment_set.all()
    blog = models.ForeignKey(Blog, related_name='comments')
    author = models.ForeignKey(UserProfile, verbose_name=u"用户")
    body = RichTextField(blank=True, null=True, verbose_name=u"内容")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created', )
        verbose_name = u"博客评论"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return 'Comment by {}'.format(self.author.username)