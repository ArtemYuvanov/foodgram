import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Load tags from JSON file'

    def handle(self, *args, **options):
        data_file = os.path.join(settings.BASE_DIR, 'data', 'tags.json')

        if not os.path.exists(data_file):
            self.stderr.write(f'Файл не найден: {data_file}')
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            tags = json.load(f)
            for tag in tags:
                Tag.objects.get_or_create(
                    name=tag['name'],
                    slug=tag['slug']
                )
        self.stdout.write(self.style.SUCCESS('Теги успешно загружены!'))
