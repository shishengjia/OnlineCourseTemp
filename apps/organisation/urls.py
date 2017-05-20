# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import OrgView, AddUserAskView, OrgHomeView, OrgCourseView, OrgDescView, OrgTeacherView, AddFavoriteView, \
    TeacherListView, TeacherDetailView, TeacherVerifyView, TeacherForumsView, TeacherCoursesView, UploadCourse, \
    UploadCourse2

_author_ = 'shishengjia'
_date_ = '09/01/2017 10:38'

urlpatterns = [
    url(r'^list/$', OrgView.as_view(), name="org_list"),
    url(r'^home/(?P<org_id>\d+)/$', OrgHomeView.as_view(), name="org_home"),
    url(r'^course/(?P<org_id>\d+)/$', OrgCourseView.as_view(), name="org_course"),
    url(r'^desc/(?P<org_id>\d+)/$', OrgDescView.as_view(), name="org_desc"),
    url(r'^org_teacher/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name="org_teacher"),

    url(r'^teacher/list$', TeacherListView.as_view(), name="teacher_list"),
    url(r'^teacher/detail/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),

    url(r'^add_ask/$', AddUserAskView.as_view(), name="add_ask"),
    url(r'^add_fav/$', AddFavoriteView.as_view(), name="add_fav"),


    url(r'^teacher_verify/$', TeacherVerifyView.as_view(), name="teacher_verify"),
    url(r'^teacher_forums/$', TeacherForumsView.as_view(), name='forum_list'),
    url(r'^teacher_courses/$', TeacherCoursesView.as_view(), name='teacher_courses'),
    url(r'^teacher_upload_course/$', UploadCourse.as_view(), name='upload_course'),
    url(r'^teacher_upload_course_2/(?P<course_id>\d+)$', UploadCourse2.as_view(), name="upload_course_2")
]