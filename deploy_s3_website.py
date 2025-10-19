#!/usr/bin/env python3
"""
S3 Static Website Deployment Script for Hackathon Demo Interface
Creates S3 bucket and configures static website hosting
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, BotoCoreError

def create_s3_bucket_and_configure_hosting():
    """Create S3 bucket and configure static website hosting"""
    
    # Configuration - Update these values for your deployment
    bucket_name = "your-demo-bucket-name"  # Change this to your desired bucket name
    region = "us-west-2"  # Change this to your preferred region
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        print(f"Creating S3 bucket: {bucket_name}")
        
        # Create bucket
        if region == 'us-east-1':
            # For us-east-1, don't specify LocationConstraint
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✓ Bucket {bucket_name} created successfully")
        
        # Configure bucket for static website hosting
        website_configuration = {
            'IndexDocument': {
                'Suffix': 'index.html'
            },
            'ErrorDocument': {
                'Key': 'error.html'
            }
        }
        
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration=website_configuration
        )
        
        print("✓ Static website hosting configured")
        
        # First, disable block public access settings
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        
        print("✓ Public access block settings configured")
        
        # Wait a moment for settings to propagate
        import time
        time.sleep(2)
        
        # Set bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print("✓ Public read access policy applied")
        
        # Get website endpoint
        website_endpoint = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
        if region == 'us-east-1':
            website_endpoint = f"http://{bucket_name}.s3-website.amazonaws.com"
        
        print(f"\n🎉 S3 static website hosting setup complete!")
        print(f"Website URL: {website_endpoint}")
        print(f"Bucket name: {bucket_name}")
        print(f"Region: {region}")
        
        # Save configuration for other scripts
        config = {
            "bucket_name": bucket_name,
            "region": region,
            "website_endpoint": website_endpoint
        }
        
        with open("s3_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✓ Configuration saved to s3_config.json")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket {bucket_name} already exists and is owned by another account")
            print("Try using a different bucket name")
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"⚠️  Bucket {bucket_name} already exists and is owned by you")
            print("Continuing with configuration...")
            # Continue with full configuration
            try:
                # Configure website hosting
                s3_client.put_bucket_website(
                    Bucket=bucket_name,
                    WebsiteConfiguration=website_configuration
                )
                print("✓ Static website hosting configured")
                
                # Configure public access
                s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': False,
                        'IgnorePublicAcls': False,
                        'BlockPublicPolicy': False,
                        'RestrictPublicBuckets': False
                    }
                )
                print("✓ Public access block settings configured")
                
                # Apply bucket policy
                import time
                time.sleep(2)
                
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }
                
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                print("✓ Public read access policy applied")
                
                # Get website endpoint and save config
                website_endpoint = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
                if region == 'us-east-1':
                    website_endpoint = f"http://{bucket_name}.s3-website.amazonaws.com"
                
                config = {
                    "bucket_name": bucket_name,
                    "region": region,
                    "website_endpoint": website_endpoint
                }
                
                with open("s3_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                print(f"✓ Configuration saved to s3_config.json")
                print(f"Website URL: {website_endpoint}")
                
                return True
            except Exception as config_error:
                print(f"❌ Error configuring existing bucket: {config_error}")
                return False
        else:
            print(f"❌ Error creating bucket: {e}")
            return False
    except BotoCoreError as e:
        print(f"❌ AWS configuration error: {e}")
        print("Please ensure AWS credentials are configured")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting S3 static website deployment...")
    success = create_s3_bucket_and_configure_hosting()
    
    if success:
        print("\n✅ S3 bucket setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ S3 bucket setup failed!")
        sys.exit(1)