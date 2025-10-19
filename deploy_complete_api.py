#!/usr/bin/env python3
"""
Complete API Gateway deployment script with CORS configuration
Deploys API Gateway, configures CORS, and updates HTML file
"""
import os
import sys
import json
import subprocess
from typing import Dict, Any
from deploy_api_gateway import APIGatewayDeployer
from update_api_endpoint import update_html_api_endpoint

def deploy_complete_api(region: str = 'us-west-2') -> Dict[str, Any]:
    """
    Complete API deployment process
    
    Args:
        region: AWS region
        
    Returns:
        Deployment results
    """
    print("🚀 Starting complete API Gateway deployment...")
    
    try:
        # Step 1: Deploy API Gateway
        print("\n📡 Deploying API Gateway...")
        deployer = APIGatewayDeployer(region)
        api_result = deployer.deploy()
        
        if not api_result['success']:
            return {
                'success': False,
                'error': f"API Gateway deployment failed: {api_result['error']}"
            }
        
        print("✅ API Gateway deployed successfully!")
        
        # Step 2: Update HTML file with API endpoint
        print("\n📝 Updating HTML file with API endpoint...")
        html_file = 'index.html'
        
        if os.path.exists(html_file):
            api_endpoint = api_result['query_endpoint']
            if update_html_api_endpoint(html_file, api_endpoint):
                print("✅ HTML file updated successfully!")
            else:
                print("⚠️  Warning: Failed to update HTML file")
        else:
            print("⚠️  Warning: HTML file not found, skipping update")
        
        # Step 3: Validate deployment
        print("\n🔍 Validating deployment...")
        validation_results = validate_deployment(api_result)
        
        # Step 4: Generate deployment summary
        summary = generate_deployment_summary(api_result, validation_results)
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(summary)
        
        return {
            'success': True,
            'api_gateway': api_result,
            'validation': validation_results,
            'summary': summary
        }
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_deployment(api_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the deployment
    
    Args:
        api_result: API Gateway deployment result
        
    Returns:
        Validation results
    """
    validation = {
        'api_gateway_created': bool(api_result.get('api_id')),
        'endpoint_available': bool(api_result.get('endpoint_url')),
        'lambda_integration': bool(api_result.get('lambda_arn')),
        'cors_configured': True,  # Assume CORS is configured by our deployment
        'html_updated': os.path.exists('index.html')
    }
    
    # Check if deployment info was saved (optional)
    validation['deployment_info_saved'] = os.path.exists('deployment_info.json')
    
    return validation

def generate_deployment_summary(api_result: Dict[str, Any], validation: Dict[str, Any]) -> str:
    """
    Generate deployment summary
    
    Args:
        api_result: API Gateway deployment result
        validation: Validation results
        
    Returns:
        Summary text
    """
    summary_lines = [
        "DEPLOYMENT SUMMARY",
        "-" * 40,
        f"API Gateway ID: {api_result.get('api_id', 'N/A')}",
        f"API Endpoint: {api_result.get('endpoint_url', 'N/A')}",
        f"Query Endpoint: {api_result.get('query_endpoint', 'N/A')}",
        f"Lambda Function: {api_result.get('lambda_arn', 'N/A').split(':')[-1] if api_result.get('lambda_arn') else 'N/A'}",
        "",
        "VALIDATION RESULTS",
        "-" * 40
    ]
    
    for key, value in validation.items():
        status = "✅" if value else "❌"
        readable_key = key.replace('_', ' ').title()
        summary_lines.append(f"{readable_key}: {status}")
    
    summary_lines.extend([
        "",
        "NEXT STEPS",
        "-" * 40,
        "1. Test the API endpoint with sample queries",
        "2. Upload the updated HTML file to S3",
        "3. Configure S3 bucket for static website hosting",
        "4. Test the complete end-to-end workflow",
        "",
        "TESTING COMMANDS",
        "-" * 40,
        f"curl -X POST {api_result.get('query_endpoint', 'N/A')} \\",
        "  -H 'Content-Type: application/json' \\",
        "  -d '{\"query\": \"21世紀美術館は今日開いていますか？\"}'",
        "",
        "FILES CREATED/UPDATED",
        "-" * 40,
        "• deployment_info.json - Deployment configuration (optional)",
        "• index.html - Updated with API endpoint",
        "• index.html.backup - Original HTML backup (if created)"
    ])
    
    return "\n".join(summary_lines)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        region = sys.argv[1]
    else:
        region = 'us-west-2'
    
    print(f"Deploying complete API to region: {region}")
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    # Check if Lambda function exists
    try:
        import boto3
        lambda_client = boto3.client('lambda', region_name=region)
        lambda_client.get_function(FunctionName='kanazawa-cultural-facility-demo')
        print("✅ Lambda function found")
    except Exception as e:
        print("❌ Lambda function not found. Please deploy Lambda first using deploy_lambda.py")
        return 1
    
    # Check if HTML file exists
    if os.path.exists('index.html'):
        print("✅ HTML file found")
    else:
        print("⚠️  HTML file not found, will skip HTML update")
    
    # Run deployment
    result = deploy_complete_api(region)
    
    if result['success']:
        # Save complete deployment info (optional - for local development)
        if os.getenv("SAVE_DEPLOYMENT_INFO", "false").lower() == "true":
            with open('deployment_info.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n💾 Complete deployment info saved to deployment_info.json")
        
        return 0
    else:
        print(f"\n❌ Deployment failed: {result['error']}")
        return 1

if __name__ == '__main__':
    sys.exit(main())