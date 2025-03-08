from django.core.management.base import BaseCommand
import json
from cms.models import Page, Category, ImpactStory, Announcement
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import CMS content from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='JSON file to import')
        parser.add_argument('--model', type=str, help='Model to import (page/category/impact/announcement)')

    def handle(self, *args, **options):
        model_map = {
            'page': Page,
            'category': Category,
            'impact': ImpactStory,
            'announcement': Announcement
        }

        model = model_map.get(options['model'])
        if not model:
            self.stdout.write(self.style.ERROR('Invalid model specified'))
            return

        with open(options['file'], 'r') as f:
            data = json.load(f)

        for item in data:
            fields = item['fields']
            if 'slug' in fields and not fields['slug']:
                fields['slug'] = slugify(fields['title'])

            try:
                obj, created = model.objects.update_or_create(
                    pk=item['pk'],
                    defaults=fields
                )
                status = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(
                    f'{status} {model.__name__} "{obj}"'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error processing {model.__name__}: {str(e)}'
                ))