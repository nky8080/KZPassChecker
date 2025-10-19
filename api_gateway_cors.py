"""
API Gateway CORS Configuration Utility
Provides consistent CORS configuration for API Gateway resources
"""
import boto3
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

class APIGatewayCORSConfig:
    """API Gateway CORS configuration manager"""
    
    def __init__(self, region: str = 'us-west-2'):
        self.region = region
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        
        # CORS configuration
        self.allowed_origins = ['*']  # Configure for production
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
    
    def configure_cors_for_resource(self, api_id: str, resource_id: str) -> None:
        """
        Configure CORS for a specific API Gateway resource
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
        """
        print(f"Configuring CORS for resource: {resource_id}")
        
        # Configure OPTIONS method for preflight requests
        self._create_options_method(api_id, resource_id)
        
        # Configure CORS headers for existing methods
        self._configure_method_cors(api_id, resource_id, 'POST')
    
    def _create_options_method(self, api_id: str, resource_id: str) -> None:
        """
        Create OPTIONS method for CORS preflight requests
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
        """
        try:
            # Create OPTIONS method
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            # Create method response
            self.apigateway_client.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': True,
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Max-Age': True
                }
            )
            
            # Create mock integration
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            
            # Create integration response with CORS headers
            self.apigateway_client.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': f"'{','.join(self.allowed_origins)}'",
                    'method.response.header.Access-Control-Allow-Headers': f"'{','.join(self.allowed_headers)}'",
                    'method.response.header.Access-Control-Allow-Methods': f"'{','.join(self.allowed_methods)}'",
                    'method.response.header.Access-Control-Max-Age': f"'{self.max_age}'"
                },
                responseTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            
            print("Created OPTIONS method for CORS preflight")
            
        except ClientError as e:
            if 'already exists' in str(e):
                print("OPTIONS method already exists, updating CORS configuration")
                self._update_options_method(api_id, resource_id)
            else:
                raise e
    
    def _update_options_method(self, api_id: str, resource_id: str) -> None:
        """
        Update existing OPTIONS method with current CORS configuration
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
        """
        try:
            # Update integration response
            self.apigateway_client.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': f"'{','.join(self.allowed_origins)}'",
                    'method.response.header.Access-Control-Allow-Headers': f"'{','.join(self.allowed_headers)}'",
                    'method.response.header.Access-Control-Allow-Methods': f"'{','.join(self.allowed_methods)}'",
                    'method.response.header.Access-Control-Max-Age': f"'{self.max_age}'"
                },
                responseTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            print("Updated OPTIONS method CORS configuration")
            
        except ClientError as e:
            print(f"Warning: Could not update OPTIONS method: {str(e)}")
    
    def _configure_method_cors(self, api_id: str, resource_id: str, http_method: str) -> None:
        """
        Configure CORS headers for a specific HTTP method
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
            http_method: HTTP method (e.g., 'POST', 'GET')
        """
        try:
            # For AWS_PROXY integration, CORS is handled by Lambda
            # But we still need to ensure method responses are configured
            for status_code in ['200', '400', '429', '500']:
                try:
                    self.apigateway_client.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod=http_method,
                        statusCode=status_code,
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Origin': True,
                            'method.response.header.Access-Control-Allow-Headers': True,
                            'method.response.header.Access-Control-Allow-Methods': True,
                            'method.response.header.Content-Type': True
                        }
                    )
                except ClientError as e:
                    if 'already exists' not in str(e):
                        print(f"Warning: Could not create method response for {status_code}: {str(e)}")
            
            print(f"Configured CORS for {http_method} method")
            
        except ClientError as e:
            print(f"Warning: Could not configure CORS for {http_method} method: {str(e)}")
    
    def validate_cors_configuration(self, api_id: str, resource_id: str) -> Dict[str, bool]:
        """
        Validate CORS configuration for a resource
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
            
        Returns:
            Validation results
        """
        results = {
            'options_method_exists': False,
            'post_method_configured': False,
            'cors_headers_configured': False
        }
        
        try:
            # Check if OPTIONS method exists
            try:
                self.apigateway_client.get_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS'
                )
                results['options_method_exists'] = True
            except ClientError:
                pass
            
            # Check if POST method exists
            try:
                self.apigateway_client.get_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='POST'
                )
                results['post_method_configured'] = True
            except ClientError:
                pass
            
            # Check CORS headers in OPTIONS integration response
            if results['options_method_exists']:
                try:
                    response = self.apigateway_client.get_integration_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        statusCode='200'
                    )
                    
                    response_params = response.get('responseParameters', {})
                    required_headers = [
                        'method.response.header.Access-Control-Allow-Origin',
                        'method.response.header.Access-Control-Allow-Headers',
                        'method.response.header.Access-Control-Allow-Methods'
                    ]
                    
                    results['cors_headers_configured'] = all(
                        header in response_params for header in required_headers
                    )
                    
                except ClientError:
                    pass
            
        except Exception as e:
            print(f"Error validating CORS configuration: {str(e)}")
        
        return results
    
    def update_allowed_origins(self, origins: List[str]) -> None:
        """
        Update allowed origins for CORS
        
        Args:
            origins: List of allowed origins
        """
        self.allowed_origins = origins
        print(f"Updated allowed origins: {origins}")
    
    def get_cors_summary(self) -> Dict[str, any]:
        """
        Get current CORS configuration summary
        
        Returns:
            CORS configuration summary
        """
        return {
            'allowed_origins': self.allowed_origins,
            'allowed_methods': self.allowed_methods,
            'allowed_headers': self.allowed_headers,
            'max_age': self.max_age
        }

def configure_api_cors(api_id: str, resource_id: str, region: str = 'us-west-2', 
                      allowed_origins: Optional[List[str]] = None) -> Dict[str, bool]:
    """
    Configure CORS for an API Gateway resource
    
    Args:
        api_id: API Gateway ID
        resource_id: Resource ID
        region: AWS region
        allowed_origins: List of allowed origins (optional)
        
    Returns:
        Configuration results
    """
    cors_config = APIGatewayCORSConfig(region)
    
    if allowed_origins:
        cors_config.update_allowed_origins(allowed_origins)
    
    # Configure CORS
    cors_config.configure_cors_for_resource(api_id, resource_id)
    
    # Validate configuration
    validation_results = cors_config.validate_cors_configuration(api_id, resource_id)
    
    print("\nCORS Configuration Summary:")
    print(f"  Allowed Origins: {cors_config.allowed_origins}")
    print(f"  Allowed Methods: {cors_config.allowed_methods}")
    print(f"  Allowed Headers: {cors_config.allowed_headers}")
    print(f"  Max Age: {cors_config.max_age} seconds")
    
    print("\nValidation Results:")
    for key, value in validation_results.items():
        status = "✅" if value else "❌"
        print(f"  {key}: {status}")
    
    return validation_results

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python api_gateway_cors.py <api_id> <resource_id> [region]")
        sys.exit(1)
    
    api_id = sys.argv[1]
    resource_id = sys.argv[2]
    region = sys.argv[3] if len(sys.argv) > 3 else 'us-west-2'
    
    print(f"Configuring CORS for API {api_id}, resource {resource_id} in {region}")
    
    results = configure_api_cors(api_id, resource_id, region)
    
    if all(results.values()):
        print("\n✅ CORS configuration completed successfully!")
    else:
        print("\n⚠️  CORS configuration completed with warnings. Check validation results above.")