# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

from DjangoUeditor.models import UEditorField
from ckeditor.fields import RichTextField

from organisation.models import CourseOrg, Teacher
from users.models import UserProfile


class Type(models.Model):
    name = models.CharField(max_length=20, verbose_name=u"课程类别")
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = u"课程类别"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class CourseManager(models.Manager):
    def get_course_lesson(self):
        # 获取课程章节
        return self.lesson_set.all()


class Course(models.Model):
    org = models.ForeignKey(CourseOrg, verbose_name=u"课程所属机构", null=True, blank=True, default="1")
    type = models.ManyToManyField(Type)
    teacher = models.ForeignKey(UserProfile, null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    # TextField不限定长度
    details = UEditorField(verbose_name=u"课程详情", width=600, height=300, imagePath="course/detail_image/",
                           filePath="course/detail_image/", default="")
    level = models.CharField(choices=(("primary", u"初级"), ("middle", u"中级"), ("advanced", u"高级")), max_length=10,
                             verbose_name=u"难度")
    learning_time = models.IntegerField(default=0, verbose_name=u"学习时长（分钟）")
    student_nums = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(upload_to="course/%Y/%m", verbose_name=u"课程封面")
    click_nums = models.IntegerField(default=0, verbose_name=u"点击量")
    price = models.IntegerField(default=0)
    notice = models.CharField(max_length=200, verbose_name=u"课前需知", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    objects = CourseManager()

    class Meta:
        verbose_name = u"课程信息"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

    def get_course_lesson(self):
        # 获取课程章节
        return self.lesson_set.all()

    def get_course_resources(self):
        return self.courseresource_set.all()

    def get_course_forums(self):
        """
        该课程的所有论坛
        """
        return self.forum_set.all()

    def get_lesson_num(self):
        return self.lesson_set.all().count()
    get_lesson_num.short_description = "章节数"


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名称")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

    def get_lesson_videos(self):
        # 获取章节下所有视频
        return self.video_set.all()


class Video(models.Model):
    STATUS_CHOICES = (
        ('unpublished', 'Unpublished'),
        ('published', 'Published')
    )
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名称")
    learning_time = models.IntegerField(default=0, verbose_name=u"学习时长（分钟）")
    url = models.CharField(max_length=500, default="", verbose_name=u"视频地址")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='unpublished')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name=u"资源文件", max_length=100)

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name


class Forum(models.Model):
    name = models.CharField(max_length=50, verbose_name=u"论坛名称")
    course = models.ForeignKey(Course)
    tag = models.ManyToManyField(Type)
    user = models.ManyToManyField(UserProfile)
    answer_student_num = models.IntegerField(default=0)
    ask_student_num = models.IntegerField(default=0)
    is_recommended = models.BooleanField(default=False)
    image = models.ImageField(upload_to="course/%Y/%m", verbose_name=u"论坛小组封面")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"论坛小组"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

    def get_student_nums(self):
        return self.answer_student_num + self.ask_student_num


class Question(models.Model):
    STATUS_CHOICES = (
        ('unsolved', 'Unsolved'),
        ('solved', 'Solved')
    )
    title = models.CharField(max_length=30, verbose_name=u'标题')
    content = RichTextField(blank=True, null=True, verbose_name=u"内容")
    questioner = models.ForeignKey(UserProfile, verbose_name=u"提问者")
    forum = models.ForeignKey(Forum, verbose_name=u"所属论坛")
    type = models.ManyToManyField(Type, verbose_name=u"问题标签")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unsolved', verbose_name=u'问题状态')
    total_view = models.PositiveIntegerField(db_index=True, default=0, verbose_name=u"浏览量")
    created_time = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = u"问题"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.title

    def get_answer_nums(self):
        return self.answer_set.all().count()


class Answer(models.Model):
    STATUS_CHOICES = (
        ('unadopted', 'Unadopted'),
        ('adopted', 'Adopted')
    )
    answer = RichTextField(blank=True, null=True)
    question = models.ForeignKey(Question, verbose_name=u"所属题目")
    answerer = models.ForeignKey(UserProfile, verbose_name=u"回答者")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='unadopted')
    created_time = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = u"回答"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.question.title


class ForumResource(models.Model):
    TYPE = (
        ('verification', 'Verification'),
        ('normal', 'Normal')
    )
    STATUS_CHOICES = (
        ('unpublished', 'Unpublished'),
        ('published', 'Published')
    )
    forum = models.ForeignKey(Forum, verbose_name=u"论坛", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=u"名称")
    file = models.FileField(upload_to="forum/resource/%Y/%m", verbose_name=u"资源文件", max_length=100)
    user = models.ForeignKey(UserProfile, verbose_name=u'上传用户')
    type = models.CharField(max_length=15, choices=TYPE, default='normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='published')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"论坛资源"
        verbose_name_plural = verbose_name


class Task(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextField(blank=True, null=True, verbose_name=u"内容")
    forum = models.ForeignKey(Forum)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程任务"
        verbose_name_plural = verbose_name

    def get_task_response_nums(self):
        return self.taskresponse_set.all().count()


class TaskResponse(models.Model):
    answer = RichTextField(blank=True, null=True)
    task = models.ForeignKey(Task, verbose_name=u'所属任务')
    answerer = models.ForeignKey(UserProfile, verbose_name=u"回答者")
    created_time = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = u"任务回答"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.task.title
