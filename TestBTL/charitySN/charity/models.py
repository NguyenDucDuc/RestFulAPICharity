from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(ModelBase):
    content = RichTextField()
    image = models.ImageField(null=True, upload_to='posts/%Y/%m')
    tags = models.ManyToManyField('Tag', related_name='tags', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']



class Tag(ModelBase):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(ModelBase):
    content = models.TextField()
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.content


class Like(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like')
    active_like = models.BooleanField(default=False)


class AuctionInfo(ModelBase):
    price = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="auction_info")

    class Meta:
        ordering = ['-price']


class Report(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reason = models.TextField(null=True)


class CommentNotification(ModelBase):
    count = models.IntegerField(default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']


class AuctionWinner(ModelBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']


class AuctionLoser(ModelBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    loser = models.ForeignKey(User, on_delete=models.CASCADE)


class LikeNotification(ModelBase):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']


class CountPost(ModelBase):
    count = models.IntegerField(null=True)
    count_comment = models.IntegerField(null=True)
    count_like = models.IntegerField(null=True)


class CountPostDetail(ModelBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    count_comment = models.IntegerField(null=True)
    count_like = models.IntegerField(null=True)


class UserStats(ModelBase):
    count_post = models.IntegerField(null=True)
    count_like = models.IntegerField(null=True)
    count_comment = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_stats')

