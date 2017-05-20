# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.db import models

from users.models import UserProfile
from courses.models import Course, Type


class UserAsk(models.Model):
    name = models.CharField(max_length=20, verbose_name=u"姓名")
    mobile = models.CharField(max_length=11, verbose_name=u"手机号")
    course_name = models.CharField(max_length=50, verbose_name=u"课程名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"用户咨询"
        verbose_name_plural = verbose_name


class CourseComment(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    course = models.ForeignKey(Course, verbose_name=u"课程")
    comment = models.CharField(max_length=200, verbose_name=u"评论")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程评论"
        verbose_name_plural = verbose_name


class UserFavorite(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    fav_id = models.IntegerField(default=0, verbose_name=u"数据ID")
    fav_type = models.IntegerField(choices=((1, "课程"), (2, "课程机构"), (3, "讲师")),
                                   default=1, verbose_name=u"收藏类型")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"用户收藏"
        verbose_name_plural = verbose_name


class UserMessage(models.Model):
    user = models.IntegerField(default=0, verbose_name=u"接收用户")
    title = models.CharField(max_length=500, verbose_name=u"消息标题", default="")
    message = models.CharField(max_length=500, verbose_name=u"消息内容")
    has_read = models.BooleanField(default=False, verbose_name=u"是否已读")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"加时间")

    class Meta:
        verbose_name = u"用户消息"
        verbose_name_plural = verbose_name


class UserCourse(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    course = models.ForeignKey(Course, verbose_name=u"课程")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"加时间")

    class Meta:
        verbose_name = u"用户课程"
        verbose_name_plural = verbose_name


class Order(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u'用户')
    course = models.ForeignKey(Course, verbose_name=u'课程')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # sort results by the publish_time field in descending order by default when we query the database.
        ordering = ('-created_time', )
        verbose_name = u"订单"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.user.username


class Questionnaire(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u'用户')
    type = models.ManyToManyField(Type, verbose_name=u"感兴趣的领域")
    is_like_answer = models.BooleanField(default=False)

    class Meta:
        verbose_name = u'问卷'
        verbose_name_plural = verbose_name