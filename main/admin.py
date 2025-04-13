from django.contrib import admin
from .models import User, Post,PostReaction,Comment,Bookmark,CommentReaction

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(PostReaction)
admin.site.register(Comment)
admin.site.register(Bookmark)
admin.site.register(CommentReaction)

