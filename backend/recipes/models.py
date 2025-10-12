from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from .constants import (
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_IMAGE_UPLOAD_PATH,
)


class Tag(models.Model):
    """Модель тега рецепта."""

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Название тега",
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
        verbose_name="Slug тега",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название ингредиента",
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to=RECIPE_IMAGE_UPLOAD_PATH,
        blank=True,
        verbose_name="Изображение рецепта",
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, "Время приготовления не меньше 1 минуты"
        )
        ],
        verbose_name="Время приготовления (в минутах)",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Список тегов",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="Список ингредиентов",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания рецепта",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления рецепта",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Количество ингредиента в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                "Количество ингредиентов должно быть не меньше 1",
            )
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        return f"{self.ingredient.name} — {self.amount}"


class UserRecipeRelation(models.Model):
    """
    Абстрактная модель для избранного и корзины,

    чтобы не дублировать поля user и recipe.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_%(class)ss",
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeRelation):
    """Избранные рецепты."""

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite",
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.recipe.name} в избранном у {self.user.username}"


class ShoppingCart(UserRecipeRelation):
    """Список покупок."""

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart",
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"{self.recipe.name} в списке покупок у {self.user.username}"
