from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name="Имя пользователя",
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    email = models.EmailField(
        unique=True, max_length=254, verbose_name="Электронная почта"
    )
    avatar = models.ImageField(
        upload_to="users/",
        blank=True,
        null=True,
        default="users/default.png",
        verbose_name="Аватар",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def clean(self):
        """Дополнительная валидация."""
        if self.username == "me":
            raise ValidationError(
                {"username": 'Имя пользователя "me" недопустимо'}
            )

    def __str__(self):
        return f"{self.username} ({self.email})"


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
        unique_together = ("user", "author")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_follow",
            )
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError({"error": "Невозможно подписаться на себя"})

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
