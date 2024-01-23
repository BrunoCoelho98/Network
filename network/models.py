from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    

class Follow(models.Model):
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')

    def __str__(self) -> str:
        return f"{self.user_following.username} is following {self.user_followed.username}"
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')

    def __str__(self) -> str:
        return f"{self.user} liked {self.post}"