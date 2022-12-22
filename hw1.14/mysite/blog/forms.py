from django import forms

comment_widget = forms.Textarea(attrs={'class': 'form-control',
                                       'id': "exampleFormControlTextarea1",
                                       "rows": 3})


class CommentForm(forms.Form):
    text = forms.CharField(max_length=400, min_length=1,
                           widget=comment_widget)


post_title_widget = forms.TextInput(attrs={"class": "form-control",
                                           "id": "exampleFormControlInput1"})

post_text_widget = forms.Textarea(attrs={"class": "form-control",
                                         "id": "exampleFormControlTextarea1",
                                         "rows": 5})


class PostForm(forms.Form):
    title = forms.CharField(label="Title", max_length=200, min_length=1,
                            widget=post_title_widget)
    text = forms.CharField(label="Text", widget=post_text_widget)
