from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):

    name = forms.CharField(
    label="",
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
        required=True
    )
    email = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}),
        required=True
    )
    body = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Comment', 'rows': 4}),
        required=True
    )
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):

    query = forms.CharField()
