from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.users.serializers import (
    AvatarSerializer,
    SubscribeSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserSubscribeRepresentSerializer,
)
from users.models import Follow

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями и подписками."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "avatar":
            return AvatarSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        """Данные текущего пользователя."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """Подписка/отписка на пользователя."""
        author = self.get_object()

        if request.method == "POST":
            serializer = SubscribeSerializer(
                data={"user": request.user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            follow = serializer.save()
            return Response(
                serializer.to_representation(follow),
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            follow = Follow.objects.filter(user=request.user, author=author)
            if not follow.exists():
                return Response(
                    {"detail": "Вы не подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """Список пользователей, на которых подписан текущий."""
        authors = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserSubscribeRepresentSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="set_password",
    )
    def set_password(self, request):
        """Смена пароля."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"errors": "Укажите current_password и new_password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"errors": "Текущий пароль неверный"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["put", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        """Добавление/удаление аватара."""
        user = request.user
        if request.method == "PUT":
            serializer = AvatarSerializer(
                user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "DELETE":
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
