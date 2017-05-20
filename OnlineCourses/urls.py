# -*- encoding: utf-8 -*-
"""OnlineCourses URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.static import serve

from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, \
    IndexView
from courses.views import CourseListView
from OnlineCourses.settings import MEDIA_ROOT
import xadmin


urlpatterns = [
    # 处理网页请求
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$', CourseListView.as_view(), name="index"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^register/$', RegisterView.as_view(), name="register"),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),

    # 遇到org开头的url，都会到organisation.urls继续完成url匹配（url的分发）
    url(r'^org/', include('organisation.urls', namespace="org")),
    # 遇到course开头的url，都会到courses.urls继续完成url匹配（url的分发）
    url(r'^course/', include('courses.urls', namespace="course")),

    url(r'^user/', include('users.urls', namespace="user")),

    url(r'^news/', include('news.urls', namespace='news')),

    #  配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),

    # ueditor相关url
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

]

# 全局404配置
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'