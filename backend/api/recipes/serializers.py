from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.users.serializers import UserSerializer
from api.utils import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit",)


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте"""

    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или обновления ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта (для избранного, корзины и подписок)."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeGetSerializer(serializers.ModelSerializer):
    """Полный сериализатор рецепта для чтения."""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientGetSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source="recipe_ingredients"
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "text",
            "cooking_time",
            "image",
        )

    def validate(self, data):
        """Проверка валидности данных"""
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Список тегов не может быть пустым."}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"tags": "Теги в рецепте должны быть уникальными."}
            )

        ingredients = data.get("recipe_ingredients", [])
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Список ингредиентов не может быть пустым."}
            )

        ingredient_ids = set()
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data["id"]
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    {
                        "ingredients": f"Ингредиент с id {ingredient_id}"
                                       f" не существует."
                    }
                )
            if ingredient_data["amount"] <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": "Количество ингредиента"
                                       " должно быть больше 0."
                    }
                )
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    {
                        "ingredients": "Ингредиенты в рецепте"
                                       " должны быть уникальными."
                    }
                )
            ingredient_ids.add(ingredient_id)

        image = data.get("image")
        if not image:
            raise serializers.ValidationError(
                {"image": "Изображение рецепта обязательно."}
            )

        return data

    def _set_tags_and_ingredients(self, recipe, tags, ingredients_data):
        """Вспомогательный метод для установки тегов и ингредиентов рецепта."""
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient["id"],
                    amount=ingredient["amount"]
                )
                for ingredient in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта с тегами и ингредиентами."""
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user,
            **validated_data
        )
        self._set_tags_and_ingredients(recipe, tags_data, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта с тегами и ингредиентами."""
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self._set_tags_and_ingredients(instance, tags_data, ingredients_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает сериализованный объект рецепта для чтения."""
        request = self.context.get("request")
        return RecipeGetSerializer(instance, context={"request": request}).data


class BaseFavoriteCartSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и корзины."""

    class Meta:
        fields = ("user", "recipe")
        extra_kwargs = {
            "user": {"read_only": True},
            "recipe": {"read_only": False},
        }

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeSmallSerializer(
            instance.recipe,
            context={"request": request}
        ).data


class FavoriteSerializer(BaseFavoriteCartSerializer):
    """Сериализатор для избранного."""

    class Meta(BaseFavoriteCartSerializer.Meta):
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в избранном",
            )
        ]


class ShoppingCartSerializer(BaseFavoriteCartSerializer):
    """Сериализатор для корзины."""

    class Meta(BaseFavoriteCartSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в корзине",
            )
        ]
