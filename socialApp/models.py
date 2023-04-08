from enum import IntEnum

from django.contrib.auth.models import (AbstractBaseUser, AbstractUser,
                                        BaseUserManager, Group, Permission,
                                        PermissionsMixin, User)
from django.db import models
from django.utils import timezone
from authentication.models import User


class DateTimeAbstactModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserStatus(IntEnum):
    SEND = 1
    ACCEPT = 2
    REJECT = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class FriendRequest(DateTimeAbstactModel):
    sender = models.ForeignKey(
        User, related_name='sent_friend_requests', null=True, blank=True, on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, related_name='received_friend_requests', null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=UserStatus.choices(), default=None, null=True, blank=True)

    def __str__(self):
        return f'Sender: {self.sender} and Receiver: {self.receiver}'
