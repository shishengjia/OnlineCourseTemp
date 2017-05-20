from django import forms

from models import Questionnaire


class QuestionnaireForm(forms.ModelForm):
    type = forms.CheckboxSelectMultiple()

    class Meta:
        model = Questionnaire
        fields = ['type', 'is_like_answer']