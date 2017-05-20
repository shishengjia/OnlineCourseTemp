# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime


from courses.models import Type


class News(models.Model):
    """
    技术文章
    """
    title = models.CharField(max_length=100, verbose_name=u'标题')
    url = models.URLField(max_length=200, verbose_name=u'链接')
    type = models.ForeignKey(Type, verbose_name=u'类型')
    descp = models.CharField(max_length=500, verbose_name=u'文章描述')
    view_nums = models.IntegerField(default=0, verbose_name=u'查看数')
    created_time = models.DateTimeField(default=datetime.now, verbose_name=u'创建时间')