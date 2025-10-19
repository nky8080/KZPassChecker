#!/usr/bin/env python3
"""
S3ウェブサイトへのHTMLファイルアップロード機能
"""
import boto3
import os
from botocore.exceptions import ClientError

def upload_html_to_s3():
    """HTMLファイルをS3ウェブサイトにアップロード"""
    print("📄 Uploading updated HTML to S3...")
    
    # S3バケット名（環境変数から取得、またはデフォルト値）
    bucket_name = os.getenv("S3_BUCKET_NAME", "your-bucket-name")
    region = os.getenv("AWS_REGION", "us-west-2")
    
    if bucket_name == "your-bucket-name":
        print("❌ Error: Please set S3_BUCKET_NAME environment variable")
        return False
    
    try:
        # S3クライアントの作成
        s3_client = boto3.client('s3', region_name=region)
        
        # HTMLファイルの存在確認
        if not os.path.exists('index.html'):
            print("❌ Error: index.html not found")
            return False
        
        # HTMLファイルをアップロード
        with open('index.html', 'rb') as f:
            s3_client.put_object(
                Bucket=bucket_name,
                Key='index.html',
                Body=f,
                ContentType='text/html',
                CacheControl='no-cache'
            )
        
        print(f"✅ Successfully uploaded index.html to {bucket_name}")
        print(f"🌐 Website URL: http://{bucket_name}.s3-website-{region}.amazonaws.com")
        
        return True
        
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = upload_html_to_s3()
    exit(0 if success else 1)