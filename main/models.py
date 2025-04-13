from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_SuperUser = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.username} joined on {self.joined_at}'
    


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    media = models.FileField(upload_to="post_media/",null=True,blank=True)
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name="authored_posts")
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    sensitive_content = models.BooleanField(default=False)


    def vote_count(self):
        return self.upvotes - self.downvotes

    def __str__(self):
        return self.title


class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='post_reactions'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='reactions'
    )
    reaction_type = models.CharField(max_length=8, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')  # Ensure a user reacts to a post only once

    def __str__(self):
        return f"{self.user.username} reacted to {self.post.title} with {self.reaction_type}"



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    agreeCount = models.PositiveIntegerField(default=0)
    disagreeCount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
class CommentReaction(models.Model):
    REACTION_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=8, choices=PostReaction.REACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'comment')  # Ensure a user reacts to a comment only once


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    #unique constraint
    class Meta:
        unique_together = ('user', 'post')
    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"