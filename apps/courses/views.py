# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.core.urlresolvers import reverse

from pure_pagination import Paginator, PageNotAnInteger

from .models import Type, Course, Video, Forum, Question, Answer, ForumResource, Task
from operation.models import UserFavorite, CourseComment, UserCourse, Order, Questionnaire
from utils.LoginJudge import LoginRequiredMixin
from utils.Redis import Redis
from .forms import AddQuestionForm, AddAnswerForm, ForumResourceForm, AddTaskForm, AddTaskResponseForm
from blog.models import Blog
from utils.RecommendedSystem import Recommended
# Create your views here.


class CourseListView(View):
    """
    课程列表
    """
    def get(self, request):
        # 所有课程
        all_course = Course.objects.all()
        # 根据收藏数筛选出所有机构中热度排名前三的机构
        hot_course = all_course.order_by("-student_nums")[:3]
        # 所有标签
        all_type = Type.objects.all()
        # 搜索课程
        key_word = request.GET.get("key_word", "")
        if key_word:
            all_course = all_course.filter(Q(name__icontains=key_word) | Q(desc__icontains=key_word))
        # 根据城市筛选，默认为空，表示选取所有机构
        type_id = request.GET.get("type", "")
        if type_id:
            type = Type.objects.get(id=type_id)
            all_course = all_course.filter(type__in=[type])
        # 根据分类（学习人数，热度,推荐）来排序
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "student_nums":
                all_course = all_course.order_by("-student_nums")
            elif sort == "hot":
                all_course = all_course.order_by("-click_nums")
            elif sort == "recommend":
                if request.user.is_authenticated:
                    # 根据用户实例化推荐类实体
                    recommend = Recommended(request.user.username)
                    # 获取推荐特征
                    types = recommend.get_recommend_types()
                    # 从所有的课程中筛选带有这些标签的课程
                    courses = []
                    for type in types:
                        courses.append(Course.objects.all().filter(type=type))
                    all_course = reduce(lambda x, y: x | y, courses)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_course, per_page=5, request=request)
        courses = p.page(page)

        return render(request, "course-list.html", {
            "all_type": all_type,  # 所有课程类别
            "courses": courses,  # 课程
            "type_id": type_id,  # 课程类别ID
            "hot_course": hot_course,  # 热门课程
            "sort": sort,  # 排序
            "section": 'course_list' # 所在页标签
        })


class MyCourseListView(LoginRequiredMixin, View):
    """
    我购买的课程列表
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        my_courses = [user_course.course for user_course in user_courses]
        # my_courses = Course.objects.filter()
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(my_courses, per_page=3, request=request)
        courses = p.page(page)

        return render(request, 'course_mycourse.html', {'courses': courses,
                                                        'section': 'my_courses'})


class CourseDetailView(View):
    """
    课程详情
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=course_id)

        # 判断课程和机构是否已被用户收藏
        has_fav_course = False
        has_fav_org = False
        has_buy = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.id), fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.org.id), fav_type=2):
                has_fav_org = True
            if Order.objects.filter(user=request.user, course=course):
                has_buy = True

        # 课程点击数加1
        course.click_nums += 1
        course.save()

        type = []
        for item in course.type.all():
            type.append(item)
        # 根据课程类别ID推荐相关课程
        recommend_course = Course.objects.all().filter(type__in=type)[1:2]

        # 追踪记录用户浏览记录
        if request.user.is_authenticated:
            r = Redis(request.user.username)
            for item in type:
                r.increase(item.name, 1)
        # 课程章节数
        lesson_num = course.lesson_set.all().count()

        # 课程所属机构教师数量
        teacher_num = course.org.teacher_set.all().count()

        # 课程所属机构课程数
        course_num = course.org.course_set.all().count()

        return render(request, "course-detail.html",{
            "course": course,   # 当前课程对象
            "lesson_num": lesson_num,
            "teacher_num": teacher_num,
            "course_num": course_num,
            "recommend_course": recommend_course,  # 推荐课程
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
            "has_buy": has_buy
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息,继承LoginRequiredMixin类，完成是否登陆的验证，没有登陆跳转到登陆界面
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        # 判断该登陆用户是否已经学过这门课，没学过的就添加到记录中,并且学习人数加1
        course_learned = UserCourse.objects.filter(user=request.user, course=course)
        if not course_learned:
            course.student_nums += 1
            course.save()
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 从UserCourse表取出所有课程为当前课程的记录
        users_course = UserCourse.objects.filter(course=course)
        # 从取出的记录中取出记录对应的用户ID(学过该门课的用户的ID)
        users_id = [users_course.user.id for users_course in users_course]
        # 根据ID从UserCourse中找出对应用户学过的所有其他课程的记录（学过该门课的用户学过的其他课程的记录）
        all_users_courses = UserCourse.objects.filter(user_id__in=users_id)
        # 从记录中遍历出相应课程ID（学过该门课的用户学过的其他课程的ID）
        courses_ids = [all_users_course.course.id for all_users_course in all_users_courses]
        # 根据ID找出对应的课程对象，并按热度排名，选出前3名
        relate_courses = Course.objects.filter(id__in=courses_ids).order_by("-click_nums")[:3]

        return render(request, "course-video.html", {
            "course": course,
            "relate_courses": relate_courses
        })


class CourseBuyView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        return render(request, 'course_buy.html', {'course': course})

    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)
        order = Order()
        order.course = course
        order.user = request.user
        return


class CourseCommentView(LoginRequiredMixin, View):
    """
    课程评论，继承LoginRequiredMixin类，完成是否登陆的验证，没有登陆跳转到登陆界面
    """
    def get(self, request, course_id):

        course = Course.objects.get(id=int(course_id))
        comments = CourseComment.objects.filter(course_id=course_id).order_by("-add_time")
        return render(request, "course-comment.html", {
            "course": course,
            "comments": comments
        })


class AddCommentView(View):
    """
    处理添加评论的请求
    """
    def post(self, request):

        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail","msg": "用户未登陆"}',
                                content_type="application/json")

        course_id = request.POST.get("course_id", 0)
        comment = request.POST.get("comment", "")
        if int(course_id) > 0 and comment:
            course_comment = CourseComment()
            course_comment.user = request.user
            course_comment.course = Course.objects.get(id=int(course_id))
            course_comment.comment = comment
            course_comment.save()
            return HttpResponse('{"status": "success","msg": "添加成功"}',
                                content_type="application/json")
        else:
            return HttpResponse('{"status": "fail","msg": "添加失败"}',
                                content_type="application/json")


class CourseVideoView(View):
    def get(self, request, video_id):

        video = Video.objects.get(id=int(video_id))

        course = video.lesson.course
        # 判断该登陆用户是否已经学过这门课，没学过的就添加到记录中
        course_learned = UserCourse.objects.filter(user=request.user, course=course)
        if not course_learned:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 从UserCourse表取出所有课程为当前课程的记录
        users_course = UserCourse.objects.filter(course=course)
        # 从取出的记录中取出记录对应的用户ID(学过该门课的用户的ID)
        users_id = [users_course.user.id for users_course in users_course]
        # 根据ID从UserCourse中找出对应用户学过的所有其他课程的记录（学过该门课的用户学过的其他课程的记录）
        all_users_courses = UserCourse.objects.filter(user_id__in=users_id)
        # 从记录中遍历出相应课程ID（学过该门课的用户学过的其他课程的ID）
        courses_ids = [all_users_course.course.id for all_users_course in all_users_courses]
        # 根据ID找出对应的课程对象，并按热度排名，选出前3名
        relate_courses = Course.objects.filter(id__in=courses_ids).order_by("-click_nums")[:3]

        return render(request, "course-play.html", {
            "course": course,
            "relate_courses": relate_courses,
            "video": video,
        })


class ForumListView(LoginRequiredMixin, View):
    """
    我的论坛列表页
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        my_courses = [user_course.course for user_course in user_courses]
        forums = [my_course.forum_set.all() for my_course in my_courses]
        forums = reduce(lambda x, y: x | y, forums)

        try:
            questionnaire = Questionnaire.objects.get(user=request.user)
            if questionnaire:
                for forum in forums:
                    if questionnaire.is_like_answer:
                        # 喜欢回答的推荐喜欢提问人数多的论坛
                        if forum.answer_student_num < forum.ask_student_num:
                            forum.is_recommended = True
                    if not questionnaire.is_like_answer:
                        # 喜欢提问的推荐喜欢回答人数多的论坛
                        if forum.answer_student_num > forum.ask_student_num:
                            forum.is_recommended = True
        except:
            pass
        return render(request, 'forum-list.html', {'forums': forums,
                                                   'section': 'course_forum'})


class ForumHomeView(LoginRequiredMixin, View):
    """
    论坛主页（问答页）
    """
    def get(self, request, forum_id):
        # 论坛ID
        forum = Forum.objects.get(id=forum_id)
        # 所有问题
        all_questions = Question.objects.filter(forum=forum)
        type = request.GET.get('type', '')
        # 根据type类型对问题进行筛选
        if type:
            if type == 'solved':
                all_questions = all_questions.filter(status='solved')
            else:
                all_questions = all_questions.filter(status='unsolved')
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_questions, per_page=5, request=request)
        questions = p.page(page)
        return render(request, 'forum-home.html', {'forum': forum,
                                                   'questions': questions})


class ForumBlogView(LoginRequiredMixin, View):
    """
    论坛手记
    """
    def get(self, request, forum_id):
        forum = Forum.objects.get(id=forum_id)
        # 所有该论坛的手记
        blogs = Blog.objects.filter(forum=forum)
        # 如果不是教师的话，则只能看到已发布的文章
        if not request.user.is_teacher:
            blogs = blogs.filter(status='published')
        return render(request, 'forum-blog.html', {'forum': forum,
                                                   'blogs': blogs})


class FormumResourceView(LoginRequiredMixin, View):
    """
    论坛资源
    """
    def get(self, request, forum_id):
        # 所在论坛
        forum = Forum.objects.get(id=forum_id)
        # 所有资源
        resources = ForumResource.objects.filter(forum=forum).filter(type='normal')
        # 如果不是该论坛所属课程的讲师，只显示已发布的资源
        if not request.user.is_teacher:
            resources = resources.filter(status='published')
        return render(request, 'forum-resource.html', {'forum': forum,
                                                       'resources': resources})


class ForumTaskView(View):
    """
    课程任务
    """
    def get(self, request, forum_id):
        forum = Forum.objects.get(id=forum_id)
        tasks = Task.objects.filter(forum=forum)
        return render(request, 'forum_task.html', {'tasks': tasks,
                                                   'forum': forum})


class ForumAddTaskView(View):
    """
    添加课程任务
    """
    def get(self, request, forum_id):
        form = AddTaskForm()
        forum = Forum.objects.get(id=forum_id)
        return render(request, 'forum_task_add.html', {'form': form,
                                    'forum': forum})

    def post(self, request, forum_id):
        form = AddTaskForm(request.POST)
        forum = Forum.objects.get(id=forum_id)
        if form.is_valid():
            task = form.save(commit=False)
            task.forum = forum
            form.save()
            return render(request, 'forum_task.html', {'forum': forum})
        return render(request, 'forum_task_add.html', {'form': form})


class ForumTaskDetailView(View):
    def get(self, request, task_id):
        task = Task.objects.get(id=task_id)
        task_answers = task.taskresponse_set.filter(task=task)
        forum = task.forum
        form = AddTaskResponseForm()
        return render(request, 'forum_task_detail.html', {'task': task,
                                                          'task_answers': task_answers,
                                                          'forum': forum,
                                                          'form': form})

    def post(self, request, task_id):
        form = AddTaskResponseForm(request.POST)
        task = Task.objects.get(id=task_id)
        task_answers = task.taskresponse_set.filter(task=task)
        forum = task.forum
        if form.is_valid():
            # 回复实体
            task_response = form.save(commit=False)
            # 赋予回复所属任务
            task_response.task = task
            # 赋予回复者
            task_response.answerer = request.user
            # 保存
            task_response.save()
            return render(request, 'forum_task_detail.html', {'task': task,
                                                              'task_answers': task_answers,
                                                              'forum': forum,
                                                              'form': form})
        return render(request, 'forum_task_detail.html', {'task': task,
                                                          'task_answers': task_answers,
                                                          'forum': forum,
                                                          'form': form})


class ForumAddQuestionView(LoginRequiredMixin, View):
    """
    提交问题
    """
    def get(self, request, forum_id):
        form = AddQuestionForm()
        forum = Forum.objects.get(id=forum_id)
        types = Type.objects.all()
        return render(request, 'forum-add-question.html', {'form': form,
                                                           'forum': forum,
                                                           'types': types})

    def post(self, request, forum_id):
        form = AddQuestionForm(request.POST)
        forum = Forum.objects.get(id=forum_id)
        if form.is_valid():
            question = form.save(commit=False)
            question.questioner = request.user
            question.forum = forum
            question.save()
            # 当保存的表单里多对多关系时，如果不是直接使用form的save方法，需要最后调用form的save_m2m方法
            form.save_m2m()
            return render(request, 'forum-home.html', {'forum': forum})
        return render(request, 'forum-add-question.html', {'form': form,
                                                           'forum': forum})


class ForumQuestionDetailView(LoginRequiredMixin, View):
    """
    问题详情
    """
    def get(self, request, question_id):
        # 问题是否已解决
        has_solved = False
        # 所在问题
        question = Question.objects.get(id=question_id)
        # 问题的所有答案
        answers = Answer.objects.filter(question=question)
        best_answer = ''
        # 如果问题已经解决，找到最佳答案，并将最佳答案从所有答案中移除
        if question.status == 'solved':
            has_solved = True
            best_answer = Answer.objects.get(status='adopted',question=question)
            answers = answers.exclude(id=best_answer.id)
        # 追踪用户记录
        r = Redis(request.user.username)
        types = question.type.all()
        for type in types:
            r.increase(type.name, 1)
        forum = question.forum
        answer_form = AddAnswerForm()
        return render(request, 'forum_question_detail.html', {'question': question,
                                                              'answers': answers,
                                                              'forum': forum,
                                                              'answer_form': answer_form,
                                                              'has_solved': has_solved,
                                                              'best_answer': best_answer})

    def post(self, request, question_id):
        # 问题是否已解决
        has_solved = False
        question = Question.objects.get(id=question_id)
        best_answer = ''
        answers = Answer.objects.filter(question=question)
        if question.status == 'solved':
            has_solved = True
            best_answer = Answer.objects.get(status='adopted')
            answers = answers.exclude(id=best_answer.id)

        answer_id = request.POST.get('answer_id', '')
        answer_form = AddAnswerForm(request.POST)
        forum = question.forum
        # 如果用户点击采纳，则问题和答案的状态相应改为solved和adopted
        if answer_id:
            answer = Answer.objects.get(id=answer_id)
            # 回答的状态置为被采纳
            answer.status = 'adopted'
            answer.save()
            # 问题的状态置为已解决
            question.status = 'solved'
            question.save()
            return render(request, 'forum_question_detail.html', {'answer_form': answer_form,
                                                                  'question': question,
                                                                  'answers': answers,
                                                                  'forum': forum,
                                                                  'has_solved': has_solved,
                                                                  'best_answer': best_answer})

        if answer_form.is_valid():
            # 创建answer实例
            answer = answer_form.save(commit=False)
            # 赋予所在问题
            answer.question = question
            # 赋予回答的用户
            answer.answerer = request.user
            answer.save()
            return render(request, 'forum_question_detail.html', {'answer_form': answer_form,
                                                                  'question': question,
                                                                  'answers': answers,
                                                                  'forum': forum,
                                                                  'has_solved': has_solved,
                                                                  'best_answer': best_answer})
        return render(request, 'forum_question_detail.html', {'answer_form': answer_form,
                                                              'question': question,
                                                              'answers': answers,
                                                              'forum': forum,
                                                              'has_solved': has_solved,
                                                              'best_answer': best_answer})


class AdoptAnswer(View):
    def post(self, request, answer_id):
        answer = Answer.objects.get(id=answer_id)
        answer.status = 'adopted'
        answer.save()
        question = answer.question
        question.status = 'solved'
        question.save()
        pass


class ForurmAddResourceView(View):
    """
    上传资源
    """
    def get(self, request, forum_id):
        form = ForumResourceForm()
        return render(request, 'forum_resource_add.html', {'form': form,
                                                           'forum_id': forum_id})

    def post(self, request, forum_id):
        form = ForumResourceForm(request.POST, request.FILES)
        forum = Forum.objects.get(id=forum_id)
        if form.is_valid():
            resource = form.save(commit=False)
            # 赋予资源发布者
            resource.user = request.user
            # 赋予所在论坛
            resource.forum = forum
            resource.save()
            return render(request, 'forum-resource.html', {'forum': forum})


class DeleteResourcesView(View):
    """
    改变资源的状态，未发布还是发布
    """
    def get(self, request, resource_id):
        resource = ForumResource.objects.get(id=resource_id)
        return render(request, 'forum_delete_resource.html', {'resource': resource})

    def post(self, request, resource_id):
        resource = ForumResource.objects.get(id=resource_id)
        forum = resource.forum
        resources = ForumResource.objects.filter(forum=forum).filter(type='normal')
        if not request.user.is_teacher:
            resources = resources.filter(status='published')
        if resource_id:
            if resource.status == 'unpublished':
                resource.status = 'published'
                resource.save()
                return render(request, 'forum-resource.html',{'forum': forum,
                                                              'resources': resources})
            if resource.status == 'published':
                resource.status = 'unpublished'
                resource.save()
                return render(request, 'forum-resource.html', {'forum': forum,
                                                               'resources': resources})

