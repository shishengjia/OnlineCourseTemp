from django import forms
from ckeditor_uploader.fields import RichTextUploadingField

from .models import Question, Answer, ForumResource, Task, TaskResponse


class AddQuestionForm(forms.ModelForm):
    content = RichTextUploadingField()

    class Meta:
        model = Question
        fields = ['type', 'title', 'content']


class AddAnswerForm(forms.ModelForm):
    answer = RichTextUploadingField()

    class Meta:
        model = Answer
        fields = ['answer']


class ForumResourceForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = ForumResource
        fields = ['name', 'file']


class AddTaskForm(forms.ModelForm):
    content = RichTextUploadingField()

    class Meta:
        model = Task
        fields = ['title', 'content']


class AddTaskResponseForm(forms.ModelForm):
    answer = RichTextUploadingField()

    class Meta:
        model = TaskResponse
        fields = ['answer']