from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
import os

def compress_image(image, quality=70, format=None):
    """
    Compress an image to reduce file size while maintaining reasonable quality.
    
    Args:
        image: Django ImageField instance
        quality: Integer from 1 to 95 (higher means better quality but larger file)
        format: Output format (None to maintain original format)
    
    Returns:
        Compressed image as ContentFile
    """
    if not image:
        return None
        
    # Open the image using PIL
    img = Image.open(image)
    
    # Determine format
    if not format:
        format = os.path.splitext(image.name)[1][1:].upper()
        if format == 'JPG':
            format = 'JPEG'
    
    # Create a BytesIO object to store the compressed image
    output = BytesIO()
    
    # Save the image to the BytesIO object with compression
    if format.upper() in ('JPEG', 'JPG'):
        # Convert to RGB if image has transparency (for JPEG)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
            img = background
        img.save(output, format=format, quality=quality, optimize=True)
    elif format.upper() == 'PNG':
        # For PNG, use optimize and different compression level
        img.save(output, format=format, optimize=True, quality=quality)
    else:
        # For other formats
        img.save(output, format=format)
    
    # Get the compressed image as bytes
    output.seek(0)
    
    # Create a ContentFile from the BytesIO object
    return ContentFile(output.getvalue())