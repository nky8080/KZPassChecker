"""
Lambda function for Kanazawa Cultural Facility Agent Demo Interface
Interfaces with Amazon Bedrock AgentCore to handle facility closure queries
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from cors_config import cors_config, create_cors_response, handle_preflight_request
from rate_limiter import check_request_rate_limit

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing facility closure queries
    
    Args:
        event: API Gateway event containing the query
        context: Lambda context
        
    Returns:
        API Gateway response with CORS headers
    """
    try:
        # Get request origin for CORS validation
        origin = event.get('headers', {}).get('Origin')
        
        # Handle preflight OPTIONS request
        if cors_config.is_preflight_request(event):
            return handle_preflight_request(origin)
        
        # Parse request body
        if not event.get('body'):
            return create_cors_response(400, {'error': 'No query provided'}, origin)
        
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return create_cors_response(400, {'error': 'Invalid request format'}, origin)
        
        query = body.get('query', '').strip()
        if not query:
            return create_cors_response(400, {'error': 'Please enter a question'}, origin)
        
        # Input validation
        if len(query) > 1000:
            return create_cors_response(400, {'error': 'Question must be 1000 characters or less'}, origin)
        
        # Rate limiting
        client_ip = get_client_ip(event)
        rate_allowed, rate_headers, rate_message = check_request_rate_limit(client_ip)
        
        if not rate_allowed:
            # Create response with rate limit headers
            response = create_cors_response(429, {
                'error': rate_message
            }, origin)
            # Add rate limit headers
            response['headers'].update(rate_headers)
            return response
        
        # Process query with AgentCore
        start_time = time.time()
        response_text = process_agent_query(query)
        response_time = round(time.time() - start_time, 2)
        
        # Return successful response with rate limit headers
        response = create_cors_response(200, {
            'response': response_text,
            'responseTime': response_time,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }, origin)
        # Add rate limit headers to show remaining quota
        response['headers'].update(rate_headers)
        return response
        
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        origin = event.get('headers', {}).get('Origin')
        return create_cors_response(500, {
            'error': 'A server error occurred. Please try again later.'
        }, origin)

def process_agent_query(query: str) -> str:
    """
    Process the query using existing AgentCore implementation from agent.py
    Falls back to enhanced Bedrock if agent.py is not available
    
    Args:
        query: User query string
        
    Returns:
        Agent response text
    """
    try:
        # Try to use the existing agent implementation
        return process_with_existing_agent(query)
        
    except ImportError as e:
        print(f"Agent import error: {str(e)}")
        print("Falling back to enhanced Bedrock implementation")
        return process_enhanced_bedrock(query)
    except Exception as e:
        print(f"Agent processing error: {str(e)}")
        print("Falling back to enhanced Bedrock implementation")
        return process_enhanced_bedrock(query)

def process_with_existing_agent(query: str) -> str:
    """
    Process query using the existing agent.py implementation
    
    Args:
        query: User query string
        
    Returns:
        Agent response text
    """
    # Import the existing agent implementation
    # This will raise ImportError if dependencies are missing
    from agent import invoke_proper
    
    # Detect language and add language instruction
    enhanced_query = detect_language_and_enhance_query(query)
    
    # Create a simple context object for the agent
    class SimpleContext:
        def __init__(self):
            self.session_id = 'demo_session'
            self.headers = {
                'X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id': 'user'
            }
    
    # Prepare payload for the agent
    payload = {
        "prompt": enhanced_query
    }
    
    context = SimpleContext()
    
    # Call the existing agent implementation
    result = invoke_proper(payload, context)
    
    # Extract response text from the result
    if isinstance(result, dict):
        if 'error' in result:
            print(f"Agent returned error: {result['error']}")
            # If agent returns an error, fall back to enhanced Bedrock
            raise Exception(f"Agent error: {result['error']}")
        elif 'response' in result:
            return result['response']
    
    # Fallback if result format is unexpected
    return str(result)

def detect_language_and_enhance_query(query: str) -> str:
    """
    Detect query language and add appropriate language instruction
    
    Args:
        query: Original user query
        
    Returns:
        Enhanced query with language instruction
    """
    # Simple language detection based on character patterns
    has_japanese = any('\u3040' <= char <= '\u309F' or  # Hiragana
                      '\u30A0' <= char <= '\u30FF' or   # Katakana
                      '\u4E00' <= char <= '\u9FAF'       # Kanji
                      for char in query)
    
    has_english = any('a' <= char.lower() <= 'z' for char in query)
    
    # Determine primary language
    if has_japanese and not has_english:
        # Pure Japanese query - no modification needed
        return query
    elif has_english and not has_japanese:
        # Pure English query - add English instruction
        return f"{query}\n\n[INSTRUCTION: Please respond in English with detailed facility information including specific dates, opening hours, and closure reasons.]"
    elif has_english and has_japanese:
        # Mixed query - determine primary language by first characters
        first_chars = query[:20]
        if any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF' for char in first_chars):
            # Starts with Japanese
            return query
        else:
            # Starts with English
            return f"{query}\n\n[INSTRUCTION: Please respond in English with detailed facility information including specific dates, opening hours, and closure reasons.]"
    else:
        # No clear language detected - default to original
        return query

def process_enhanced_bedrock(query: str) -> str:
    """
    Enhanced Bedrock implementation with session-like memory simulation
    
    Args:
        query: User query string
        
    Returns:
        Agent response text
    """
    try:
        # Use Claude 3.7 Sonnet for better responses (similar to AgentCore)
        region = os.getenv('AWS_REGION', 'us-west-2')
        bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        
        # Enhanced system prompt with comprehensive facility information (18 facilities)
        system_prompt = """You are a knowledgeable assistant specializing in cultural facilities covered by the Kanazawa Cultural Forest Pass (文化の森お出かけパス) in Ishikawa Prefecture, Japan. You provide information about all 18 official facilities.

OFFICIAL FACILITIES (18 facilities from the Cultural Forest Pass):

**Core Museums & Cultural Sites:**
1. **D.T. Suzuki Museum (鈴木大拙館)** - Generally closed Mondays (open on holidays), 9:30-17:00
2. **21st Century Museum of Contemporary Art, Kanazawa** - Generally open 10:00-18:00 (Fri/Sat until 20:00), closed Mondays except holidays
3. **Ishikawa Living Craft Museum (いしかわ生活工芸ミュージアム)** - Traditional crafts display
4. **Nomura Samurai House (武家屋敷跡 野村家)** - Historic samurai residence
5. **Seisonkaku (国指定重要文化財 成巽閣)** - Important Cultural Property
6. **Ishikawa Prefectural Museum of History** - 9:00-17:00, closed Mondays
7. **National Crafts Museum (国立工芸館)** - National museum for crafts
8. **Kenrokuen Garden (特別名勝 兼六園)** - Open year-round, one of Japan's three great gardens
9. **Kanazawa Castle Park** - Historic castle grounds

**Specialized Museums:**
10. **Maeda Tosanokami Family Museum (前田土佐守家資料館)** - Closed Mondays (open on holidays)
11. **Kanazawa Shinise Memorial Hall (金沢市老舗記念館)** - Traditional merchant house, closed Mondays
12. **Ishikawa Prefectural Museum of Art** - 9:30-18:00, closed Mondays
13. **Kanazawa Kurashi Museum (金沢くらしの博物館)** - Lifestyle museum, closed Mondays
14. **Kanazawa Noh Museum** - 9:00-17:00, closed Mondays
15. **Nakamura Memorial Museum (金沢市立中村記念美術館)** - 9:30-17:00, closed Mondays
16. **Kaga Honda Museum (加賀本多博物館)** - Samurai family museum
17. **Kanazawa Furusato Ijin-kan (金沢ふるさと偉人館)** - Local heroes museum
18. **Ishikawa Shiko Memorial Cultural Exchange Hall (石川四高記念文化交流館)** - Cultural exchange facility

GENERAL PATTERNS:
- Most facilities: Closed Mondays (except national holidays), open holidays with Tuesday closure
- Winter closure: December 29 - January 3 for most facilities
- Hours: Generally 9:00-17:00 or 9:30-17:00 (entry 30 minutes before closing)
- Special exhibitions may affect schedules

RESPONSE GUIDELINES:
- Provide specific information about these 18 official Cultural Forest Pass facilities
- For current status or special events, always advise checking official websites
- Mention that this is part of the Cultural Forest Pass system
- Be conversational and informative
- Respond in the language the user asks in (Japanese or English)
- If asked about facilities not in this list, clarify these are the 18 official pass facilities"""

        # Detect language and create appropriate user message
        has_japanese = any('\u3040' <= char <= '\u309F' or  # Hiragana
                          '\u30A0' <= char <= '\u30FF' or   # Katakana
                          '\u4E00' <= char <= '\u9FAF'       # Kanji
                          for char in query)
        
        has_english = any('a' <= char.lower() <= 'z' for char in query)
        
        if has_english and not has_japanese:
            # English query - add English instruction
            user_message = f"Question: {query}\n\nPlease respond in English with specific information about the facility's status on the requested date, including opening hours, closure reasons, and any special events."
        else:
            # Japanese or mixed query - use original format
            user_message = f"Question: {query}"
        
        # Use Claude 3.7 Sonnet for higher quality responses
        model_id = os.getenv('MODEL_ID', 'us.anthropic.claude-3-7-sonnet-20250219-v1:0')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 400,  # Increased for more detailed responses
            "temperature": 0.3,  # Lower temperature for more consistent responses
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            return "Sorry, I couldn't generate a response."
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Enhanced Bedrock error ({error_code}): {str(e)}")
        
        if error_code == 'AccessDeniedException':
            return "Access denied. Please contact the system administrator."
        elif error_code == 'ThrottlingException':
            return "Too many requests. Please wait and try again later."
        elif error_code == 'ValidationException':
            # Fallback to Haiku if Sonnet is not available
            return process_bedrock_fallback(query)
        else:
            return "A service error occurred. Please try again later."
            
    except Exception as e:
        print(f"Enhanced Bedrock processing error: {str(e)}")
        return process_bedrock_fallback(query)

def process_bedrock_fallback(query: str) -> str:
    """
    Fallback to direct Bedrock when AgentCore is not available
    
    Args:
        query: User query string
        
    Returns:
        Agent response text
    """
    try:
        # Use Bedrock directly as fallback
        region = os.getenv('AWS_REGION', 'us-west-2')
        bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        
        # Create a simple prompt for facility information
        system_prompt = """You are an assistant that provides information about cultural facilities in Kanazawa City, Japan.
Please answer questions about the following facilities:
- 21st Century Museum of Contemporary Art, Kanazawa
- Kenrokuen Garden
- Ishikawa Prefectural Museum of Art
- Kanazawa Noh Museum
- D.T. Suzuki Museum
- Nakamura Memorial Museum
- Ishikawa Prefectural Museum of History

Provide general opening hours and closure information. For specific dates, please advise users to "check the official website for the latest information." Always respond in English."""

        # For fallback, always use simple format since it's already English-focused
        user_message = f"Question: {query}"
        
        # Use Claude 3 Haiku for cost-effective responses
        model_id = os.getenv('FALLBACK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            return "Sorry, I couldn't generate a response."
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Bedrock error ({error_code}): {str(e)}")
        
        if error_code == 'AccessDeniedException':
            return "Access denied. Please contact the system administrator."
        elif error_code == 'ThrottlingException':
            return "Too many requests. Please wait and try again later."
        else:
            return "A service error occurred. Please try again later."
            
    except Exception as e:
        print(f"Bedrock fallback processing error: {str(e)}")
        return "An error occurred during processing. Please try again later."

# CORS response function is now imported from cors_config.py

def get_client_ip(event: Dict[str, Any]) -> str:
    """
    Extract client IP address from API Gateway event
    
    Args:
        event: API Gateway event
        
    Returns:
        Client IP address
    """
    # Try to get real IP from headers (if behind proxy/CloudFront)
    headers = event.get('headers', {})
    
    # Check common proxy headers
    for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
        if header in headers:
            ip = headers[header].split(',')[0].strip()
            if ip:
                return ip
    
    # Fallback to source IP
    request_context = event.get('requestContext', {})
    return request_context.get('identity', {}).get('sourceIp', 'unknown')

# Rate limiting functions moved to rate_limiter.py module