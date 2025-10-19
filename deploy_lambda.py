#!/usr/bin/env python3
"""
Deployment script for Kanazawa Cultural Facility Agent Lambda function
Creates deployment package and uploads to AWS Lambda
"""
import os
import sys
import zipfile
import boto3
import json
from pathlib import Path
from typing import List, Dict, Any

class LambdaDeployer:
    """Lambda function deployment manager"""
    
    def __init__(self, region: str = 'us-west-2'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
        # Configuration
        self.function_name = 'kanazawa-cultural-facility-demo'
        self.handler = 'lambda_handler.lambda_handler'
        self.runtime = 'python3.9'
        self.timeout = 30
        self.memory_size = 512
        
        # Files to include in deployment package
        self.include_files = [
            'lambda_handler.py',
            'cors_config.py',
            'rate_limiter.py',
            'agent.py',
            'config.py',
            'facility_scraper.py'
        ]
    
    def create_deployment_package(self, package_path: str = 'lambda_deployment.zip') -> str:
        """
        Create deployment package for Lambda function
        
        Args:
            package_path: Path for the deployment package
            
        Returns:
            Path to created package
        """
        print("Creating Lambda deployment package...")
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add Python files
            for file_name in self.include_files:
                if os.path.exists(file_name):
                    zip_file.write(file_name, file_name)
                    print(f"  Added: {file_name}")
                else:
                    print(f"  Warning: {file_name} not found")
            
            # Add requirements if they exist
            if os.path.exists('lambda_requirements.txt'):
                zip_file.write('lambda_requirements.txt', 'requirements.txt')
                print("  Added: requirements.txt")
        
        print(f"Deployment package created: {package_path}")
        return package_path
    
    def create_execution_role(self) -> str:
        """
        Create IAM execution role for Lambda function
        
        Returns:
            Role ARN
        """
        role_name = f"{self.function_name}-execution-role"
        
        # Trust policy for Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Try to get existing role
            response = self.iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"Using existing execution role: {role_arn}")
            return role_arn
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create new role
            print(f"Creating execution role: {role_name}")
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Execution role for {self.function_name} Lambda function"
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach basic execution policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach Bedrock access policy
            bedrock_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock:InvokeModel",
                            "bedrock:InvokeModelWithResponseStream"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='BedrockAccess',
                PolicyDocument=json.dumps(bedrock_policy)
            )
            
            print(f"Created execution role: {role_arn}")
            return role_arn
    
    def deploy_function(self, package_path: str, role_arn: str) -> Dict[str, Any]:
        """
        Deploy Lambda function
        
        Args:
            package_path: Path to deployment package
            role_arn: Execution role ARN
            
        Returns:
            Lambda function configuration
        """
        print(f"Deploying Lambda function: {self.function_name}")
        
        with open(package_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            # Try to update existing function
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                ZipFile=zip_content
            )
            print("Updated existing Lambda function")
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = self.lambda_client.create_function(
                FunctionName=self.function_name,
                Runtime=self.runtime,
                Role=role_arn,
                Handler=self.handler,
                Code={'ZipFile': zip_content},
                Description='Kanazawa Cultural Facility Agent Demo API',
                Timeout=self.timeout,
                MemorySize=self.memory_size,
                Environment={
                    'Variables': {
                        'CORS_ALLOWED_ORIGINS': '*',  # Configure for production
                        'BEDROCK_AGENTCORE_MEMORY_ID': os.getenv('BEDROCK_AGENTCORE_MEMORY_ID', '')
                    }
                }
            )
            print("Created new Lambda function")
        
        return response
    
    def deploy(self) -> Dict[str, Any]:
        """
        Full deployment process
        
        Returns:
            Deployment result
        """
        try:
            # Create deployment package
            package_path = self.create_deployment_package()
            
            # Create execution role
            role_arn = self.create_execution_role()
            
            # Deploy function
            function_config = self.deploy_function(package_path, role_arn)
            
            # Clean up deployment package
            os.remove(package_path)
            print(f"Cleaned up deployment package: {package_path}")
            
            print("\n✅ Deployment completed successfully!")
            print(f"Function Name: {function_config['FunctionName']}")
            print(f"Function ARN: {function_config['FunctionArn']}")
            print(f"Runtime: {function_config['Runtime']}")
            print(f"Handler: {function_config['Handler']}")
            
            return {
                'success': True,
                'function_name': function_config['FunctionName'],
                'function_arn': function_config['FunctionArn'],
                'role_arn': role_arn
            }
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {str(e)}")
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
    
    print(f"Deploying to region: {region}")
    
    deployer = LambdaDeployer(region)
    result = deployer.deploy()
    
    if result['success']:
        print("\nNext steps:")
        print("1. Create API Gateway and connect to this Lambda function")
        print("2. Configure CORS settings in API Gateway")
        print("3. Deploy API Gateway stage")
        print("4. Update S3 website to use the API endpoint")
        
        # Save deployment info (optional - for local development)
        if os.getenv("SAVE_DEPLOYMENT_INFO", "false").lower() == "true":
            with open('deployment_info.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\nDeployment info saved to deployment_info.json")
    
    return 0 if result['success'] else 1

if __name__ == '__main__':
    sys.exit(main())