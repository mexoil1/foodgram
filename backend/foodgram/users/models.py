from django.db import models
from django.contrib.auth.models import AbstractUser
from api.constants import Constants


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        unique=True,
        max_length=Constants.MAX_USER_USERNAME,
        verbose_name='Username')
    email = models.EmailField(
        unique=True,
        max_length=Constants.MAX_USER_USERNAME,
        verbose_name='Email')
    first_name = models.CharField(
        max_length=Constants.MAX_USER_FIRST_NAME,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=Constants.MAX_USER_LAST_NAME,
        verbose_name='Фамилия')

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
