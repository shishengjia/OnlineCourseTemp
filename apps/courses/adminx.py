# -*- encoding: utf-8 -*-

from .models import Course, Lesson, Video, CourseResource, Type, Forum, ForumResource
from operation.models import Order
import xadmin

_author_ = 'shishengjia'
_date_ = '05/01/2017 13:02'


class CourseAdmin(object):
    # 后台界面显示的字段
    list_display = ['name', 'price', 'get_lesson_num', 'level', 'learning_time', 'student_nums',
                    'fav_nums', 'image', 'add_time']
    # 可供搜索的字段
    search_fields = ['name', 'desc', 'details', 'level', 'student_nums',
                     'fav_nums', 'image', 'click_nums']
    # 可供查找的字段
    list_filter = ['name', 'desc', 'details', 'level', 'learning_time', 'student_nums',
                   'fav_nums', 'image', 'click_nums', 'add_time']
    # 设置默认排序规则
    ordering = ['-click_nums']
    # 设置只读字段
    readonly_fields = ['click_nums', 'fav_nums']
    # 设置不显示的字段，但是要注意不能跟readonly_fields里的字段重复，否则会冲突
    exclude = []
    # 设置能直接在列表页直接修改的字段
    list_editable = ['level']
    style_fields = {"details": "ueditor"}

    def save_models(self):
        # 保存课程的时候统计机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.org is not None:
            course_org = obj.org
            course_org.course_nums = Course.objects.filter(org=course_org).count()
            course_org.save()


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 注意搜索外键字段的格式course__字段名
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'url', 'learning_time', 'name', 'add_time']
    search_fields = ['lesson', 'url', 'learning_time',  'name']
    list_filter = ['lesson__name', 'url', 'learning_time',  'name', 'add_time']


class TypeAdmin(object):
    list_display = ['name', 'add_time']
    search_fields = ['name']
    list_filter = ['name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'add_time', 'download']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'add_time', 'download']


class ForumAdmin(object):
    list_display = ['name', 'answer_student_num', 'ask_student_num']


class ForumResourceAdmin(object):
    list_display = ['name', 'type', 'user']
    list_filter = ['type']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(Type, TypeAdmin)
xadmin.site.register(Forum, ForumAdmin)
xadmin.site.register(ForumResource, ForumResourceAdmin)