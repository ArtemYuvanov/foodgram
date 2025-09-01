import json
from django.core.management.base import BaseCommand
from app.models import Tag


class Command(BaseCommand):
    help = 'Load tags from JSON file'

    def handle(self, *args, **options):
        with open('data/tags.json', 'r', encoding='utf-8') as f:
            tags = json.load(f)
            for tag in tags:
                Tag.objects.get_or_create(
                    name=tag['name'],
                    color=tag['color'],
                    slug=tag['slug']
                )
        self.stdout.write(self.style.SUCCESS('Теги успешно загружены!'))
