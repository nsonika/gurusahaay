"""
Cloudinary Service - Handles file uploads to Cloudinary.

Supports:
- Video uploads
- Document uploads (PDF, DOC, etc.)
- Image uploads
"""
import cloudinary
import cloudinary.uploader
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


class CloudinaryService:
    """
    Handles file uploads to Cloudinary CDN.
    """
    
    @staticmethod
    def is_configured() -> bool:
        """Check if Cloudinary is properly configured."""
        return bool(
            settings.cloudinary_cloud_name and 
            settings.cloudinary_api_key and 
            settings.cloudinary_api_secret
        )
    
    @staticmethod
    def upload_video(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "gurusahaay/videos"
    ) -> Dict[str, Any]:
        """
        Upload a video file to Cloudinary.
        
        Args:
            file_path: Path to the video file or base64 data
            public_id: Optional custom public ID
            folder: Cloudinary folder to store in
            
        Returns:
            Dict with upload result including 'secure_url', 'public_id', etc.
        """
        if not CloudinaryService.is_configured():
            raise ValueError("Cloudinary is not configured. Please set CLOUDINARY_* env variables.")
        
        options = {
            "resource_type": "video",
            "folder": folder,
            "overwrite": True,
        }
        
        if public_id:
            options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **options)
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "duration": result.get("duration"),
            "bytes": result.get("bytes"),
            "resource_type": "video"
        }
    
    @staticmethod
    def upload_document(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "gurusahaay/documents"
    ) -> Dict[str, Any]:
        """
        Upload a document (PDF, DOC, etc.) to Cloudinary.
        
        Args:
            file_path: Path to the document file or base64 data
            public_id: Optional custom public ID
            folder: Cloudinary folder to store in
            
        Returns:
            Dict with upload result including 'secure_url', 'public_id', etc.
        """
        if not CloudinaryService.is_configured():
            raise ValueError("Cloudinary is not configured. Please set CLOUDINARY_* env variables.")
        
        options = {
            "resource_type": "raw",  # For non-image/video files
            "folder": folder,
            "overwrite": True,
        }
        
        if public_id:
            options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **options)
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
            "resource_type": "raw"
        }
    
    @staticmethod
    def upload_image(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "gurusahaay/images"
    ) -> Dict[str, Any]:
        """
        Upload an image to Cloudinary.
        
        Args:
            file_path: Path to the image file or base64 data
            public_id: Optional custom public ID
            folder: Cloudinary folder to store in
            
        Returns:
            Dict with upload result including 'secure_url', 'public_id', etc.
        """
        if not CloudinaryService.is_configured():
            raise ValueError("Cloudinary is not configured. Please set CLOUDINARY_* env variables.")
        
        options = {
            "resource_type": "image",
            "folder": folder,
            "overwrite": True,
        }
        
        if public_id:
            options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **options)
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes"),
            "resource_type": "image"
        }
    
    @staticmethod
    def upload_file(
        file_path: str,
        file_type: str,
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file based on its type.
        
        Args:
            file_path: Path to the file or base64 data
            file_type: Type of file ('video', 'document', 'image')
            public_id: Optional custom public ID
            
        Returns:
            Dict with upload result
        """
        if file_type == "video":
            return CloudinaryService.upload_video(file_path, public_id)
        elif file_type == "document":
            return CloudinaryService.upload_document(file_path, public_id)
        elif file_type == "image":
            return CloudinaryService.upload_image(file_path, public_id)
        else:
            # Default to raw upload
            return CloudinaryService.upload_document(file_path, public_id)
    
    @staticmethod
    def delete_file(public_id: str, resource_type: str = "image") -> bool:
        """
        Delete a file from Cloudinary.
        
        Args:
            public_id: The public ID of the file to delete
            resource_type: Type of resource ('image', 'video', 'raw')
            
        Returns:
            True if deleted successfully
        """
        if not CloudinaryService.is_configured():
            return False
        
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception:
            return False
