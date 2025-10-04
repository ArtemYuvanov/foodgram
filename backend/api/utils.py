import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.response import Response


class Base64ImageField(serializers.ImageField):
    """
    Поле для приёма изображения, закодированного в base64.
    Конвертирует строку 'data:image/png;base64,...' в Django ContentFile.
    """

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError(
                "Изображение рецепта обязательно."
            )

        if isinstance(data, bytes):
            return super().to_internal_value(data)

        if isinstance(data, str):
            if "base64," in data:
                header, data = data.split("base64,")
            try:
                decoded_file = base64.b64decode(data)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    "Некорректные данные изображения (не base64)."
                )

            file_ext = imghdr.what(None, decoded_file)
            if file_ext is None:
                if "jpeg" in header or "jpg" in header:
                    file_ext = "jpg"
                else:
                    raise serializers.ValidationError(
                        "Не удалось определить формат изображения."
                    )

            file_name = f"{uuid.uuid4()}.{file_ext}"
            data = ContentFile(decoded_file, name=file_name)
            return super().to_internal_value(data)

        raise serializers.ValidationError(
            "Неподдерживаемый тип данных для изображения."
        )


def create_model_instance(request, recipe, serializer_class):
    """Добавление в favorite или shopping_cart"""
    serializer = serializer_class(
        data={"user": request.user.id, "recipe": recipe.id},
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_class, recipe, error_message):
    """Удаление из favorite или shopping_cart"""
    instance = model_class.objects.filter(user=request.user, recipe=recipe)
    if not instance.exists():
        return Response(
            {"errors": error_message}, status=status.HTTP_400_BAD_REQUEST
        )
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
