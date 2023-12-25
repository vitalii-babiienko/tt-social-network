from django.contrib import admin

from post.models import Hashtag, Post, Comment

admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Comment)
