from django import forms
from ckeditor_uploader.fields import RichTextUploadingField

from .models import Blog, BlogComment


class AddBlogForm(forms.ModelForm):
    body = RichTextUploadingField()

    class Meta:
        model = Blog
        fields = ['type', 'title', 'body']


class BlogCommentForm(forms.ModelForm):
    body = RichTextUploadingField()

    class Meta:
        model = BlogComment
        fields = ['body']
