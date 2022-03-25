from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_subject(self):
        posted = self.cleaned_data['text']
        if posted == '':
            raise forms.ValidationError(
                'Вы должны обязательно что-то написать',
                params={'posted': posted},
            )
        return posted


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError(
                'Вы должны обязательно что-то написать',
                params={'text': text},
            )
        return text
