import datetime

from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    pub_date = models.DateTimeField()
    hide = models.BooleanField(default=False)
    num_views = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    text = models.CharField(max_length=400)
    pub_date = models.DateTimeField(default=datetime.datetime.now())
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.text[:20]
