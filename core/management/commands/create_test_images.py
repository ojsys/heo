from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import SliderImage, GalleryImage
import requests

class Command(BaseCommand):
    help = 'Creates test slider and gallery images'

    def handle(self, *args, **kwargs):
        # Test image URL (replace with your own test images)
        test_image_url = "https://picsum.photos/800/600"

        # Create slider images
        for i in range(3):
            response = requests.get(test_image_url)
            if response.status_code == 200:
                slider = SliderImage(
                    title=f'Slider Image {i+1}',
                    caption=f'Caption for slider image {i+1}',
                    order=i
                )
                slider.image.save(f'slider_{i+1}.jpg', ContentFile(response.content), save=True)
                self.stdout.write(f'Created slider image {i+1}')

        # Create gallery images
        categories = ['education', 'healthcare', 'housing', 'community']
        for i in range(6):
            response = requests.get(test_image_url)
            if response.status_code == 200:
                gallery = GalleryImage(
                    title=f'Gallery Image {i+1}',
                    description=f'Description for gallery image {i+1}',
                    category=categories[i % len(categories)],
                    order=i
                )
                gallery.image.save(f'gallery_{i+1}.jpg', ContentFile(response.content), save=True)
                self.stdout.write(f'Created gallery image {i+1}')