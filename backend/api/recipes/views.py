from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.recipes.filters import IngredientFilter, RecipeFilter
from api.recipes.permissions import IsAdminAuthorOrReadOnly
from api.recipes.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from api.utils import create_model_instance, delete_model_instance
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов. Только чтение."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов. Только чтение."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD рецептов + избранное + список покупок"""

    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Возвращает queryset с предзагрузкой и аннотациями."""
        user = (
            self.request.user if self.request.user.is_authenticated else None
        )

        queryset = Recipe.objects.select_related("author").prefetch_related(
            "tags",
            "recipe_ingredients__ingredient"
        )

        if user:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef("pk"))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef("pk")
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=False,
                is_in_shopping_cart=False
            )
        return queryset

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от action"""
        if self.action in ["list", "retrieve"]:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            return create_model_instance(request, recipe, FavoriteSerializer)
        elif request.method == "DELETE":
            error_message = "У вас нет этого рецепта в избранном"
            return delete_model_instance(
                request, Favorite, recipe, error_message
            )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из корзины."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            return create_model_instance(
                request, recipe, ShoppingCartSerializer
            )
        elif request.method == "DELETE":
            error_message = "У вас нет этого рецепта в списке покупок"
            return delete_model_instance(
                request, ShoppingCart, recipe, error_message
            )

    def _generate_shopping_cart_file(self, user):
        """Генерация текста списка покупок для пользователя."""
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__in_shopping_carts__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )
        lines = ["Список покупок:\n"]
        for ingredient in ingredients:
            ingredient_name = ingredient["ingredient__name"]
            total_amount = ingredient["total_amount"]
            measurement_unit = ingredient["ingredient__measurement_unit"]
            lines.append(
                f"{ingredient_name} - {total_amount}, {measurement_unit}"
            )
        return "\n".join(lines)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок пользователя."""
        file_content = self._generate_shopping_cart_file(request.user)
        response = HttpResponse(file_content, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="get-link",
    )
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f"/s/{recipe.id}/")
        return Response({"short-link": short_url})
