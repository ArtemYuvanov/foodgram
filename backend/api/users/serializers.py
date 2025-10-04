from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.utils import Base64ImageField
from users.models import Follow


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Регистрация пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Информация о пользователе"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class UserSubscribeRepresentSerializer(UserSerializer):
    """Отображение пользователя с подписками"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit") if request else None
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[: int(limit)]
        return [
            {
                "id": r.id,
                "name": r.name,
                "image": r.image.url if r.image else None,
                "cooking_time": r.cooking_time,
            }
            for r in queryset
        ]

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка/отписка на автора"""

    class Meta:
        model = Follow
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны на этого пользователя",
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["author"]:
            raise serializers.ValidationError(
                "Нельзя подписываться на самого себя!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return UserSubscribeRepresentSerializer(
            instance.author, context={"request": request}
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Аватар пользователя"""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ["avatar"]

    def validate(self, data):
        request = self.context.get("request")
        if request and request.method == "PUT" and "avatar" not in data:
            raise serializers.ValidationError(
                {"avatar": ["Это поле обязательно."]}
            )
        return data
