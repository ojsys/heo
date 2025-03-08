from django.core.management.base import BaseCommand
import json
from cms.models import Page, Category, ImpactStory, Announcement
from django.core.serializers.json import DjangoJSONEncoder

class Command(BaseCommand):
    help = 'Export CMS content to JSON files'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, help='Model to export (page/category/impact/announcement)')
        parser.add_argument('--output', type=str, help='Output file path')

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

        queryset = model.objects.all()
        data = []
        for obj in queryset:
            obj_data = {
                'model': obj._meta.model_name,
                'pk': obj.pk,
                'fields': {
                    field.name: getattr(obj, field.name)
                    for field in obj._meta.fields
                    if not field.is_relation
                }
            }
            data.append(obj_data)

        output_file = options['output'] or f'cms_{options["model"]}_export.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, cls=DjangoJSONEncoder, indent=2)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported to {output_file}'))