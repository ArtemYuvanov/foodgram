from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField('Имя',
                                  max_length=150)
    last_name = models.CharField('Фамилия',
                                 max_length=150)
    email = models.EmailField('Email',
                              unique=True,
                              max_length=200)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # constraints = [
        #     models.UniqueConstraint(fields=('username', 'email'),
        #                             name='unique_user')
        # ]

    def clean(self):
        if self.username == 'me':
            raise ValidationError(
                {'error': 'Невозможно создать пользователя с именем me'}
            )

    def __str__(self):
        return self.username


class Follow(models.Model):
    username = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Автор'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=(
        #             "username",
        #             "author",
        #         ),
        #         name="unique_follow",)
        # ]

    def clean(self):
        if self.username == self.author:
            raise ValidationError(
                {'error': 'Невозможно подписаться на себя'}
            )

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'
