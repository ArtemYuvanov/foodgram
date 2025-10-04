from django.db.models import Sum
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
    """Теги доступны только для чтения"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты доступны только для чтения"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD рецептов + избранное + список покупок"""

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "delete"]

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

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__in_shopping_carts__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        lines = ["Список покупок:\n"]
        for ing in ingredients:
            lines.append(
                f"{ing['ingredient__name']} - {ing['total_amount']}, "
                f"{ing['ingredient__measurement_unit']}"
            )
        response = HttpResponse("\n".join(lines), content_type="text/plain")
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
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f"/s/{recipe.id}/")
        return Response({"short-link": short_url})
