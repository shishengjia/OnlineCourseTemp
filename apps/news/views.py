# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View

from pure_pagination import Paginator, PageNotAnInteger

from .models import News
from courses.models import Type
from utils.Redis import Redis
from utils.RecommendedSystem import Recommended


class NewsListView(View):
    """
    新闻列表s
    """
    def get(self, request):
        all_news = News.objects.all()
        hot_news = News.objects.order_by('-view_nums')[:3]
        all_type = Type.objects.all()

        type_id = request.GET.get("type", "")
        if type_id:
            type = Type.objects.get(id=type_id)
            all_news = all_news.filter(type=type)

        sort = request.GET.get("sort", "")
        if sort:
            if sort == 'hot':
                all_news = all_news.order_by('-view_nums')
            if sort == 'recommend':
                if request.user.is_authenticated():
                    recommend = Recommended(request.user.username)
                    types = recommend.get_recommend_types()
                    news = []
                    for type in types:
                        news.append(News.objects.all().filter(type=type))
                    # 使用 | 操作符链接list里的queryset
                    all_news = reduce(lambda x, y: x | y, news)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_news, per_page=20, request=request)
        newses = p.page(page)

        return render(request, 'forum-news-list.html', {'newses': newses,
                                                        'hot_news': hot_news,
                                                        'section': 'news',
                                                        'all_type': all_type,
                                                        'type_id': type_id})


class NewsTrackView(View):
    """
    中间处理过程，在记录用户行为后跳转到相应页面
    """
    def get(self, request, news_id):
        news = News.objects.get(id=news_id)

        # 追踪用户记录
        if request.user.is_authenticated():
            r = Redis(request.user.username)
            r.increase(news.type.name, 1)

        return HttpResponseRedirect(news.url)
