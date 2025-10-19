#!/usr/bin/env python3
"""
API Gateway deployment script for Kanazawa Cultural Facility Agent Demo
Creates REST API with POST endpoint and integrates with Lambda function
"""
import os
import sys
import json
import boto3
import time
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from api_gateway_cors import configure_api_cors

class APIGatewayDeployer:
    """API Gateway deployment manager"""
    
    def __init__(self, region: str = 'us-west-2'):
        self.region = region
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
        # Configuration
        self.api_name = 'kanazawa-cultural-facility-demo-api'
        self.api_description = 'API for Kanazawa Cultural Facility Agent Demo'
        self.stage_name = 'prod'
        self.lambda_function_name = 'kanazawa-cultural-facility-demo'
    
    def _get_allowed_origins(self) -> list:
        """
        Get allowed origins for CORS configuration
        
        Returns:
            List of allowed origins
        """
        # Get from environment variable or use defaults
        env_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if env_origins:
            return [origin.strip() for origin in env_origins.split(',')]
        
        # Default origins for demo (configure for production)
        return [
            '*',  # Allow all origins for demo
            # 'https://your-s3-bucket.s3-website-YOUR_REGION.amazonaws.com',
            # 'https://your-custom-domain.com'
        ]
    
    def get_lambda_function_arn(self) -> str:
        """
        Get Lambda function ARN
        
        Returns:
            Lambda function ARN
        """
        try:
            response = self.lambda_client.get_function(
                FunctionName=self.lambda_function_name
            )
            return response['Configuration']['FunctionArn']
        except ClientError as e:
            raise Exception(f"Lambda function not found: {self.lambda_function_name}. Please deploy Lambda first.")
    
    def create_rest_api(self) -> str:
        """
        Create REST API
        
        Returns:
            API ID
        """
        print(f"Creating REST API: {self.api_name}")
        
        try:
            response = self.apigateway_client.create_rest_api(
                name=self.api_name,
                description=self.api_description,
                endpointConfiguration={
                    'types': ['REGIONAL']
                },
                policy=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "execute-api:Invoke",
                            "Resource": "*"
                        }
                    ]
                })
            )
            
            api_id = response['id']
            print(f"Created REST API: {api_id}")
            return api_id
            
        except ClientError as e:
            if 'already exists' in str(e):
                # Find existing API
                apis = self.apigateway_client.get_rest_apis()
                for api in apis['items']:
                    if api['name'] == self.api_name:
                        print(f"Using existing REST API: {api['id']}")
                        return api['id']
            raise e
    
    def get_root_resource_id(self, api_id: str) -> str:
        """
        Get root resource ID
        
        Args:
            api_id: API Gateway ID
            
        Returns:
            Root resource ID
        """
        response = self.apigateway_client.get_resources(restApiId=api_id)
        for resource in response['items']:
            if resource['path'] == '/':
                return resource['id']
        raise Exception("Root resource not found")
    
    def create_query_resource(self, api_id: str, parent_id: str) -> str:
        """
        Create /query resource
        
        Args:
            api_id: API Gateway ID
            parent_id: Parent resource ID
            
        Returns:
            Query resource ID
        """
        print("Creating /query resource")
        
        try:
            response = self.apigateway_client.create_resource(
                restApiId=api_id,
                parentId=parent_id,
                pathPart='query'
            )
            
            resource_id = response['id']
            print(f"Created /query resource: {resource_id}")
            return resource_id
            
        except ClientError as e:
            if 'already exists' in str(e):
                # Find existing resource
                resources = self.apigateway_client.get_resources(restApiId=api_id)
                for resource in resources['items']:
                    if resource.get('pathPart') == 'query':
                        print(f"Using existing /query resource: {resource['id']}")
                        return resource['id']
            raise e
    
    def create_post_method(self, api_id: str, resource_id: str, lambda_arn: str) -> None:
        """
        Create POST method for queries with CORS support
        
        Args:
            api_id: API Gateway ID
            resource_id: Resource ID
            lambda_arn: Lambda function ARN
        """
        print("Creating POST method with CORS support")
        
        # Lambda integration URI
        lambda_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        try:
            # Create method
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE',
                requestParameters={}
            )
            
            # Create method responses for different status codes
            for status_code in ['200', '400', '429', '500']:
                try:
                    self.apigateway_client.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
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
                        raise e
            
            # Create integration (AWS_PROXY handles CORS automatically via Lambda)
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            print("Created POST method with Lambda integration and CORS support")
            
        except ClientError as e:
            if 'already exists' in str(e):
                print("POST method already exists, updating integration")
                # Update integration
                self.apigateway_client.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='POST',
                    type='AWS_PROXY',
                    integrationHttpMethod='POST',
                    uri=lambda_uri
                )
            else:
                raise e
    

    
    def grant_lambda_permission(self, api_id: str, lambda_arn: str) -> None:
        """
        Grant API Gateway permission to invoke Lambda
        
        Args:
            api_id: API Gateway ID
            lambda_arn: Lambda function ARN
        """
        print("Granting Lambda invoke permission to API Gateway")
        
        # Extract function name from ARN
        function_name = lambda_arn.split(':')[-1]
        
        # Get account ID for the source ARN
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        
        # Source ARN for the permission
        source_arn = f"arn:aws:execute-api:{self.region}:{account_id}:{api_id}/*/POST/query"
        
        try:
            self.lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'apigateway-invoke-{api_id}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=source_arn
            )
            print("Lambda permission granted")
            
        except ClientError as e:
            if 'already exists' in str(e):
                print("Lambda permission already exists")
            else:
                raise e
    
    def deploy_api(self, api_id: str) -> str:
        """
        Deploy API to stage
        
        Args:
            api_id: API Gateway ID
            
        Returns:
            API endpoint URL
        """
        print(f"Deploying API to stage: {self.stage_name}")
        
        try:
            self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName=self.stage_name,
                stageDescription='Production stage for demo',
                description=f'Deployment at {time.strftime("%Y-%m-%d %H:%M:%S")}'
            )
            
        except ClientError as e:
            if 'already exists' in str(e):
                # Update existing deployment
                deployments = self.apigateway_client.get_deployments(restApiId=api_id)
                if deployments['items']:
                    deployment_id = deployments['items'][0]['id']
                    self.apigateway_client.update_stage(
                        restApiId=api_id,
                        stageName=self.stage_name,
                        patchOps=[
                            {
                                'op': 'replace',
                                'path': '/deploymentId',
                                'value': deployment_id
                            }
                        ]
                    )
            else:
                raise e
        
        endpoint_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/{self.stage_name}"
        print(f"API deployed successfully: {endpoint_url}")
        return endpoint_url
    
    def deploy(self) -> Dict[str, Any]:
        """
        Full API Gateway deployment process
        
        Returns:
            Deployment result
        """
        try:
            print("Starting API Gateway deployment...")
            
            # Get Lambda function ARN
            lambda_arn = self.get_lambda_function_arn()
            print(f"Lambda function ARN: {lambda_arn}")
            
            # Create REST API
            api_id = self.create_rest_api()
            
            # Get root resource
            root_resource_id = self.get_root_resource_id(api_id)
            
            # Create /query resource
            query_resource_id = self.create_query_resource(api_id, root_resource_id)
            
            # Create POST method
            self.create_post_method(api_id, query_resource_id, lambda_arn)
            
            # Configure CORS for the resource
            print("Configuring CORS for API Gateway...")
            allowed_origins = self._get_allowed_origins()
            cors_results = configure_api_cors(api_id, query_resource_id, self.region, allowed_origins)
            
            if not all(cors_results.values()):
                print("⚠️  Warning: CORS configuration may be incomplete")
            
            # Grant Lambda permission
            self.grant_lambda_permission(api_id, lambda_arn)
            
            # Deploy API
            endpoint_url = self.deploy_api(api_id)
            
            print("\n✅ API Gateway deployment completed successfully!")
            print(f"API ID: {api_id}")
            print(f"Endpoint URL: {endpoint_url}")
            print(f"Query endpoint: {endpoint_url}/query")
            
            return {
                'success': True,
                'api_id': api_id,
                'endpoint_url': endpoint_url,
                'query_endpoint': f"{endpoint_url}/query",
                'lambda_arn': lambda_arn
            }
            
        except Exception as e:
            print(f"\n❌ API Gateway deployment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Main deployment function"""
    if len(sys.argv) > 1:
        region = sys.argv[1]
    else:
        region = 'us-west-2'
    
    print(f"Deploying API Gateway to region: {region}")
    
    deployer = APIGatewayDeployer(region)
    result = deployer.deploy()
    
    if result['success']:
        print("\nNext steps:")
        print("1. Update S3 website to use the API endpoint")
        print("2. Test the API endpoint with sample queries")
        print("3. Configure custom domain (optional)")
        
        # Save deployment info (optional - for local development)
        if os.getenv("SAVE_DEPLOYMENT_INFO", "false").lower() == "true":
            deployment_info = {}
            if os.path.exists('deployment_info.json'):
                with open('deployment_info.json', 'r') as f:
                    deployment_info = json.load(f)
            
            deployment_info.update({
                'api_gateway': result
            })
            
            with open('deployment_info.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)
            print("\nDeployment info updated in deployment_info.json")
    
    return 0 if result['success'] else 1

if __name__ == '__main__':
    sys.exit(main())