import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Добавляем ингредиенты из файла CSV."""

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv',
                            nargs='?', type=str)

    def handle(self, *args, **options):
        data_file = os.path.join(
            settings.BASE_DIR,
            'data',
            options['filename']
        )

        if not os.path.exists(data_file):
            raise CommandError(f'Файл {data_file} не найден!')

        with open(data_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 2:
                    continue
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )

        self.stdout.write(
            self.style.SUCCESS('=== Ингредиенты успешно загружены ===')
        )
