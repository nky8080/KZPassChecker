"""
CORS Configuration for Kanazawa Cultural Facility Agent Demo
Provides secure CORS headers for S3 static website access
"""
import os
from typing import Dict, List, Optional

class CORSConfig:
    """CORS configuration management"""
    
    def __init__(self):
        # Get allowed origins from environment or use defaults
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ['POST', 'OPTIONS']
        self.allowed_headers = [
            'Content-Type',
            'X-Amz-Date',
            'Authorization',
            'X-Api-Key',
            'X-Amz-Security-Token',
            'X-Requested-With'
        ]
        self.max_age = 86400  # 24 hours
        
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed origins from environment variables"""
        # Production origins from environment
        env_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if env_origins:
            return [origin.strip() for origin in env_origins.split(',')]
        
        # Default origins for development
        return [
            'https://*.s3.amazonaws.com',
            'https://*.s3-website-*.amazonaws.com',
            'http://localhost:3000',  # Local development
            'http://127.0.0.1:3000'   # Local development
        ]
    
    def get_cors_headers(self, origin: Optional[str] = None) -> Dict[str, str]:
        """
        Get CORS headers for response
        
        Args:
            origin: Request origin to validate
            
        Returns:
            Dictionary of CORS headers
        """
        # Validate origin
        allowed_origin = self._validate_origin(origin)
        
        headers = {
            'Access-Control-Allow-Origin': allowed_origin,
            'Access-Control-Allow-Methods': ', '.join(self.allowed_methods),
            'Access-Control-Allow-Headers': ', '.join(self.allowed_headers),
            'Access-Control-Max-Age': str(self.max_age),
            'Vary': 'Origin'
        }
        
        # Add security headers
        headers.update(self._get_security_headers())
        
        return headers
    
    def _validate_origin(self, origin: Optional[str]) -> str:
        """
        Validate request origin against allowed origins
        
        Args:
            origin: Request origin
            
        Returns:
            Validated origin or '*' for wildcard
        """
        if not origin:
            return '*'
        
        # Check exact matches
        if origin in self.allowed_origins:
            return origin
        
        # Check wildcard patterns
        for allowed in self.allowed_origins:
            if '*' in allowed:
                pattern = allowed.replace('*', '.*')
                import re
                if re.match(pattern, origin):
                    return origin
        
        # Default to wildcard for demo purposes
        # In production, return specific origin or reject
        return '*'
    
    def _get_security_headers(self) -> Dict[str, str]:
        """
        Get additional security headers
        
        Returns:
            Dictionary of security headers
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
    
    def is_preflight_request(self, event: Dict) -> bool:
        """
        Check if request is a CORS preflight request
        
        Args:
            event: API Gateway event
            
        Returns:
            True if preflight request
        """
        return (
            event.get('httpMethod') == 'OPTIONS' and
            event.get('headers', {}).get('Access-Control-Request-Method') is not None
        )

# Global CORS configuration instance
cors_config = CORSConfig()

def create_cors_response(status_code: int, body: Dict, origin: Optional[str] = None) -> Dict:
    """
    Create API Gateway response with CORS headers
    
    Args:
        status_code: HTTP status code
        body: Response body
        origin: Request origin
        
    Returns:
        API Gateway response with CORS headers
    """
    import json
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json; charset=utf-8',
            **cors_config.get_cors_headers(origin)
        },
        'body': json.dumps(body, ensure_ascii=False)
    }

def handle_preflight_request(origin: Optional[str] = None) -> Dict:
    """
    Handle CORS preflight OPTIONS request
    
    Args:
        origin: Request origin
        
    Returns:
        Preflight response
    """
    return create_cors_response(200, {'message': 'OK'}, origin)