from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponse


# Create your models here.

class Log(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.modify_time}"


class Profile(Log):
    GENDER_CHOICES = [("m", "man"), ("f", "female"), ("o", "other"), ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_user")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(max_length=300, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    photo = models.ImageField(upload_to="static/Profile/%s", null=True, blank=True)
    is_active = models.BooleanField(default=False)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    protected_profile = models.BooleanField(default=False)

    fg = models.ManyToManyField(User, related_name="fg", blank=True, default=None)
    fw = models.ManyToManyField(User, related_name="fw", blank=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]

    # def save(self, *args, **kwargs):
    #     print("Profile model save")
    #     if self.fg and self.fw is None:
    #         return super().save(self, *args, **kwargs)
    #
    #     if self.fg.username == self.fw.username:
    #         print("in condution")
    #         raise ValueError("khedet ro nemitooni !! FOLLOW !! koni azizam")
    #

    def __str__(self):
        return f"{self.user.username}, id: {self.id}"


class Post(Log):
    post_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_profile", db_index=True)

    caption = models.TextField(max_length=300, null=True, blank=True)
    Location = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to="static/Profile/%s", null=True, blank=True)
    comment_is_active = models.BooleanField(default=True)
    is_archaive = models.BooleanField(default=False)  # if True post not availabe in profile

    like = models.ManyToManyField(User, blank=True)

    class Meta:
        indexes = [models.Index(fields=["caption"]),
                   ]

    def __str__(self):
        return f"{self.post_profile},{self.caption[:10]} , id:{self.id}"


class Comment(Log):
    commnet_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment_post")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")

    body = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.commnet_post}: {self.body[:20]}, id: {self.id}"


class FollowPendingRequests(Log):
    follow_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_receiver")
    follow_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_sender")

    def save(self, *args, **kwargs):
        print("FollowPendingRequests model save")

        if self.follow_receiver.username == self.follow_sender.username:
            raise ValueError("khedet ro nemitooni !! FOLLOW !! koni azizam")
        else:
            return super().save(self, *args, **kwargs)

    def __str__(self):
        return f", id: {self.id}"
