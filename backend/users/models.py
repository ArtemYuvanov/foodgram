from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from .constants import (
    AVATAR_UPLOAD_PATH,
    DEFAULT_AVATAR_PATH,
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator],
        verbose_name="Имя пользователя",
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        verbose_name="Фамилия",
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name="Электронная почта",
    )
    avatar = models.ImageField(
        upload_to=AVATAR_UPLOAD_PATH,
        blank=True,
        default=DEFAULT_AVATAR_PATH,
        verbose_name="Аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.username} ({self.email})"

    def clean(self):
        """Дополнительная валидация."""
        if self.username == "me":
            raise ValidationError(
                {"username": 'Имя пользователя "me" недопустимо'}
            )


class Follow(models.Model):
    """Подписки пользователей друг на друга."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    def clean(self):
        if self.user == self.author:
            raise ValidationError({"error": "Невозможно подписаться на себя"})
