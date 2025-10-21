import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from typing import List, Optional
from fastapi import UploadFile, HTTPException

# Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dmlqq3wpe"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "778645464188285"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


async def upload_image(file: UploadFile, folder: str = "ovees_jewelry") -> dict:
    """
    Upload an image to Cloudinary
    
    Args:
        file: The uploaded file
        folder: Cloudinary folder to store the image
    
    Returns:
        dict with secure_url, public_id, and optimized_url
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="auto",
            transformation=[
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        
        # Get optimized URL
        optimized_url, _ = cloudinary_url(
            upload_result["public_id"],
            fetch_format="auto",
            quality="auto"
        )
        
        return {
            "secure_url": upload_result["secure_url"],
            "public_id": upload_result["public_id"],
            "optimized_url": optimized_url,
            "width": upload_result.get("width"),
            "height": upload_result.get("height")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


async def upload_multiple_images(files: List[UploadFile], folder: str = "ovees_jewelry") -> List[dict]:
    """
    Upload multiple images to Cloudinary
    
    Args:
        files: List of uploaded files
        folder: Cloudinary folder to store the images
    
    Returns:
        List of dicts with image information
    """
    uploaded_images = []
    
    for file in files:
        result = await upload_image(file, folder)
        uploaded_images.append(result)
    
    return uploaded_images


def delete_image(public_id: str) -> dict:
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: The public ID of the image to delete
    
    Returns:
        Result of the deletion
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image deletion failed: {str(e)}")


def get_optimized_url(public_id: str, width: Optional[int] = None, height: Optional[int] = None) -> str:
    """
    Get an optimized URL for an image
    
    Args:
        public_id: The public ID of the image
        width: Optional width for transformation
        height: Optional height for transformation
    
    Returns:
        Optimized URL
    """
    transformations = {
        'fetch_format': 'auto',
        'quality': 'auto'
    }
    
    if width:
        transformations['width'] = width
    if height:
        transformations['height'] = height
    if width and height:
        transformations['crop'] = 'auto'
        transformations['gravity'] = 'auto'
    
    optimized_url, _ = cloudinary_url(public_id, **transformations)
    return optimized_url


def get_thumbnail_url(public_id: str, width: int = 300, height: int = 300) -> str:
    """
    Get a thumbnail URL for an image
    
    Args:
        public_id: The public ID of the image
        width: Thumbnail width (default: 300)
        height: Thumbnail height (default: 300)
    
    Returns:
        Thumbnail URL
    """
    thumbnail_url, _ = cloudinary_url(
        public_id,
        width=width,
        height=height,
        crop="fill",
        gravity="auto",
        fetch_format="auto",
        quality="auto"
    )
    return thumbnail_url
