# -*- encoding: utf-8 -*-
from django.conf.urls import url, include

from .views import CourseListView, CourseDetailView, CourseInfoView, CourseCommentView, AddCommentView, \
    CourseVideoView, ForumListView, ForumHomeView, FormumResourceView, ForumBlogView, ForumAddQuestionView, \
    ForumQuestionDetailView, MyCourseListView, ForurmAddResourceView, DeleteResourcesView, \
    CourseBuyView, ForumTaskView, ForumAddTaskView, ForumTaskDetailView, AdoptAnswer
_author_ = 'shishengjia'
_date_ = '13/01/2017 16:17'


urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name="course_list"),
    url(r'^my_course/$', MyCourseListView.as_view(), name="my_course_list"),
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="course_detail"),
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name="course_info"),
    url(r'^comment/(?P<course_id>\d+)/$', CourseCommentView.as_view(), name="course_comment"),
    url(r'^add_comment/$', AddCommentView.as_view(), name="add_comment"),
    url(r'^video/(?P<video_id>\d+)/$', CourseVideoView.as_view(), name="course_video"),
    url(r'^buy/(?P<course_id>\d+)$', CourseBuyView.as_view(), name="course_buy"),
    #  论坛相关
    url(r'^forum/$', ForumListView.as_view(), name="forum_list"),
    url(r'^forum/(?P<forum_id>\d+)/home/$', ForumHomeView.as_view(), name="forum_home"),
    url(r'^forum/(?P<forum_id>\d+)/resource/$', FormumResourceView.as_view(), name="forum_resource"),
    url(r'^forum/(?P<forum_id>\d+)/add_resource/$', ForurmAddResourceView.as_view(), name='forum_add_resource'),
    url(r'^forum/(?P<forum_id>\d+)/blog/$', ForumBlogView.as_view(), name="forum_blog"),
    url(r'^forum/(?P<forum_id>\d+)/task/$', ForumTaskView.as_view(), name="forum_task"),
    url(r'^forum/task_datail/(?P<task_id>\d+)/$', ForumTaskDetailView.as_view(), name="forum_task_detail"),
    url(r'^forum/(?P<forum_id>\d+)/add_task/$', ForumAddTaskView.as_view(), name="forum_add_task"),
    url(r'^forum/(?P<forum_id>\d+)/add_question/$', ForumAddQuestionView.as_view(),
        name="forum_add_question"),
    url(r'^forum/question/(?P<question_id>\d+)/$', ForumQuestionDetailView.as_view(), name="forum_question_detail"),
    url(r'^forum/adopt_answer/(?P<answer_id>\d+)/$', AdoptAnswer.as_view(), name="forum_adopt_answer"),
    url(r'^forum/delete_resource/(?P<resource_id>\d+)/$', DeleteResourcesView.as_view(), name="forum_delete_resource"),
    # 博客相关
    url(r'^blog/', include('blog.urls', namespace="blog")),
]
