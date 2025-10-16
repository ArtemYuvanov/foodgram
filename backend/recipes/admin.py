from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.db.models import Count, Prefetch

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class AuthorFilter(AutocompleteFilter):
    """Фильтр с автопоиском по автору."""

    title = "Автор"
    field_name = "author"


class TagFilter(AutocompleteFilter):
    """Фильтр с автопоиском по тегам."""

    title = "Тег"
    field_name = "tags"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ("name", "slug")
    list_display_links = ("name",)
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = ("name", "measurement_unit")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class IngredientInRecipeInline(admin.TabularInline):
    """Встроенный компонент для ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = 1
    min_num = 1
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = ("name", "author", "favorite_count")
    list_display_links = ("name",)
    list_filter = (AuthorFilter, TagFilter)
    search_fields = ("name",)
    inlines = (IngredientInRecipeInline,)
    ordering = ("-id",)

    def get_queryset(self, request):
        """Оптимизация запросов."""
        queryset = (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related(
                Prefetch("tags"),
                Prefetch("ingredients"),
            )
            .annotate(favorite_count=Count("favorited_by"))
        )
        return queryset


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = (AuthorFilter,)
    ordering = ("-id",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка корзины покупок."""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    ordering = ("-id",)
