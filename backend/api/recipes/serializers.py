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
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientGetSerializer(serializers.ModelSerializer):
    """Для чтения ингредиентов в рецепте"""

    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientPostSerializer(serializers.ModelSerializer):
    """Для создания/обновления рецепта с ингредиентами"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Краткое отображение рецепта (для избранного, подписок и т.п.)"""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientGetSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientPostSerializer(
        many=True, source="recipe_ingredients"
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

        ids = set()
        for ing in ingredients:
            ing_id = ing["id"]
            if not Ingredient.objects.filter(id=ing_id).exists():
                raise serializers.ValidationError(
                    {"ingredients": f"Ингредиент с id {ing_id} не существует."}
                )
            if ing["amount"] <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": "Количество ингредиента "
                        "должно быть больше 0."
                    }
                )
            if ing_id in ids:
                raise serializers.ValidationError(
                    {
                        "ingredients": "Ингредиенты в рецепте"
                        " должны быть уникальными."
                    }
                )
            ids.add(ing_id)

        image = data.get("image")
        if not image:
            raise serializers.ValidationError(
                {"image": "Изображение рецепта обязательно."}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("recipe_ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        recipe.tags.set(tags)
        for ing in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe, ingredient_id=ing["id"], amount=ing["amount"]
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("recipe_ingredients", None)
        tags = validated_data.pop("tags", None)

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            IngredientInRecipe.objects.filter(recipe=instance).delete()
            for ing in ingredients:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=ing["id"],
                    amount=ing["amount"],
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeGetSerializer(instance, context={"request": request}).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в избранном",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeSmallSerializer(
            instance.recipe, context={"request": request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в корзине",
            )
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeSmallSerializer(
            instance.recipe, context={"request": request}
        ).data
