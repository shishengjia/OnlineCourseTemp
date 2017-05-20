# -*- encoding: utf-8 -*-
from django.conf.urls import url

from .views import NewsListView, NewsTrackView

urlpatterns = [
    # 处理网页请求
    url(r'^list/$', NewsListView.as_view(), name="news_list"),
    url(r'^track/(?P<news_id>\d+)$', NewsTrackView.as_view(), name="news_track")
]

