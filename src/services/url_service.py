"""URL validation and processing service."""
import re


class URLService:
    """Service for URL validation and normalization."""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        url = url.strip()
        return url.startswith("http://") or url.startswith("https://")
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize and trim URL.
        
        Args:
            url: URL string to normalize
            
        Returns:
            Normalized URL
        """
        url = url.strip()
        
        # Remove trailing slash if present (optional)
        # url = url.rstrip('/')
        
        return url
    
    @staticmethod
    def deduplicate_urls(urls: list) -> list:
        """
        Remove duplicate URLs while preserving order.
        
        Args:
            urls: List of URLs
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        result = []
        for url in urls:
            normalized = URLService.normalize_url(url)
            if normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result

