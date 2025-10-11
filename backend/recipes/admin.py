from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
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
    list_display = ("id", "name", "author", "favorite_count")
    list_filter = ("tags", "author")
    search_fields = ("name", "author__username")
    inlines = (IngredientInRecipeInline,)
    ordering = ("-id",)

    def favorite_count(self, obj):
        return obj.favorited_by.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    ordering = ("-id",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    ordering = ("-id",)
