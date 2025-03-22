from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings
from .utils import compress_image
import os

# List of models with image fields to compress
IMAGE_MODELS = {
    'wagtailimages.Image': ['file'],  # Wagtail images if you're using Wagtail
    # Add your application models with image fields here, for example:
    # 'applications.Document': ['document'],  # Adjust based on your actual model and field names
}

@receiver(pre_save)
def compress_images_on_save(sender, instance, **kwargs):
    """
    Signal handler to compress images before saving.
    """
    # Get the model name in the format 'app_label.ModelName'
    model_name = f"{sender._meta.app_label}.{sender.__name__}"
    
    # Check if this model is in our list of models to compress
    if model_name in IMAGE_MODELS:
        # Get the list of image fields for this model
        image_fields = IMAGE_MODELS[model_name]
        
        # Process each image field
        for field_name in image_fields:
            # Get the image field
            image_field = getattr(instance, field_name, None)
            
            # Check if the image field has a file and it's an image
            if image_field and hasattr(image_field, 'file'):
                # Get the file extension
                file_ext = os.path.splitext(image_field.name)[1].lower()
                
                # Only compress image files
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    # Get the original file name
                    original_name = os.path.basename(image_field.name)
                    
                    # Compress the image
                    compressed_image = compress_image(
                        image_field, 
                        quality=getattr(settings, 'IMAGE_COMPRESSION_QUALITY', 70)
                    )
                    
                    if compressed_image:
                        # Save the compressed image back to the field
                        image_field.save(original_name, compressed_image, save=False)