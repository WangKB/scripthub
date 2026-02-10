#!/usr/bin/env python3
"""
Dreamina Image Generator
A simple CLI tool to generate images using ByteDance Volcengine Dreamina API.

Usage:
    python dreamina_gen.py --prompt "a beautiful sunset" --output ./sunset.png
    
Environment Variables:
    VOLCENGINE_AK: Access Key ID
    VOLCENGINE_SK: Secret Access Key
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone


def sign(key, msg):
    """HMAC-SHA256 signing helper."""
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(secret_key, date_stamp, region_name, service_name):
    """Generate signature key following AWS Signature Version 4."""
    k_date = sign(('VCT' + secret_key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'request')
    return k_signing


def build_request_headers(access_key, secret_key, region, service, method, uri, query, body):
    """
    Build HTTP headers with Volcengine API signature.
    Following https://www.volcengine.com/docs/6369/67269
    """
    # Generate timestamp
    now = datetime.now(timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    
    # Calculate body hash
    if body:
        payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    else:
        payload_hash = hashlib.sha256(b'').hexdigest()
    
    # Build canonical request headers
    host = f'open.volcengineapi.com'
    
    headers = {
        'host': host,
        'x-date': amz_date,
        'x-content-sha256': payload_hash,
        'content-type': 'application/json' if body else 'application/x-www-form-urlencoded'
    }
    
    # Create signed headers string
    signed_headers = ';'.join(sorted(headers.keys()))
    
    # Build canonical request
    canonical_headers = ''.join([f'{k}:{v}\n' for k, v in sorted(headers.items())])
    
    canonical_request = (
        method + '\n' +
        uri + '\n' +
        query + '\n' +
        canonical_headers + '\n' +
        signed_headers + '\n' +
        payload_hash
    )
    
    # Build string to sign
    algorithm = 'VCT-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/request'
    string_to_sign = (
        algorithm + '\n' +
        amz_date + '\n' +
        credential_scope + '\n' +
        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    )
    
    # Calculate signature
    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Build authorization header
    auth_header = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )
    
    headers['authorization'] = auth_header
    
    return headers


def call_volcengine_api(access_key, secret_key, action, version, body_dict, region='cn-north-1', service='cv'):
    """
    Call Volcengine API with proper authentication.
    
    Args:
        access_key: Your AK
        secret_key: Your SK  
        action: API action name
        version: API version
        body_dict: Request body as dict
        region: Region (default: cn-north-1)
        service: Service name (default: cv for computer vision)
    
    Returns:
        Response JSON as dict
    """
    method = 'POST'
    uri = '/'
    
    # Build query string
    query_params = {
        'Action': action,
        'Version': version
    }
    query = '&'.join([f'{k}={urllib.parse.quote_plus(str(v))}' for k, v in sorted(query_params.items())])
    
    body = json.dumps(body_dict) if body_dict else ''
    
    headers = build_request_headers(
        access_key, secret_key, region, service,
        method, uri, query, body
    )
    
    url = f'https://open.volcengineapi.com/?{query}'
    
    req = urllib.request.Request(
        url,
        data=body.encode('utf-8') if body else None,
        headers=headers,
        method=method
    )
    
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))


def generate_image(prompt, output_path, access_key, secret_key, width=1024, height=1024, seed=None):
    """
    Generate an image using Dreamina AI API.
    
    Args:
        prompt: Text prompt describing the image
        output_path: Path to save the generated image
        access_key: Volcengine Access Key
        secret_key: Volcengine Secret Key
        width: Image width (default: 1024)
        height: Image height (default: 1024)
        seed: Random seed for reproducibility (optional)
    """
    # Dreamina Image Generation API parameters
    # Based on documentation at https://www.volcengine.com/docs/85621/1817045
    body = {
        "req_key": "high_aes_general_v21_L",  # Model version
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed if seed is not None else int(time.time() * 1000) % 1000000000,
        "use_seed": True,
        "return_url": True,  # Return URL instead of base64
        "logo_info": {
            "add_logo": False
        }
    }
    
    print(f"Generating image for prompt: '{prompt}'")
    print(f"Image size: {width}x{height}")
    
    # Call the API
    response = call_volcengine_api(
        access_key=access_key,
        secret_key=secret_key,
        action='CVProcess',
        version='2022-08-31',
        body_dict=body,
        service='cv'
    )
    
    # Parse response
    if 'data' not in response:
        print(f"Error: Unexpected response format: {json.dumps(response, indent=2)}")
        sys.exit(1)
    
    data = response['data']
    
    # Check for image URL or base64 data
    image_url = data.get('image_url')
    image_b64 = data.get('image')
    
    if image_url:
        # Download image from URL
        print(f"Downloading image from: {image_url}")
        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            image_data = response.read()
    elif image_b64:
        # Decode base64
        image_data = base64.b64decode(image_b64)
    else:
        print(f"Error: No image data in response: {json.dumps(data, indent=2)}")
        sys.exit(1)
    
    # Save image
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(image_data)
    
    print(f"Image saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate images using ByteDance Volcengine Dreamina AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Environment Variables:
  VOLCENGINE_AK    Your Volcengine Access Key ID
  VOLCENGINE_SK    Your Volcengine Secret Access Key

Examples:
  python dreamina_gen.py -p "a beautiful sunset over mountains" -o sunset.png
  python dreamina_gen.py -p "cute cat wearing glasses" -o ./images/cat.png -W 1024 -H 1024
        '''
    )
    
    parser.add_argument('-p', '--prompt', required=True,
                        help='Text prompt describing the image to generate')
    parser.add_argument('-o', '--output', required=True,
                        help='Output file path for the generated image')
    parser.add_argument('-W', '--width', type=int, default=1024,
                        help='Image width in pixels (default: 1024)')
    parser.add_argument('-H', '--height', type=int, default=1024,
                        help='Image height in pixels (default: 1024)')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='Random seed for reproducibility (optional)')
    parser.add_argument('--ak', default=os.environ.get('VOLCENGINE_AK'),
                        help='Access Key (or set VOLCENGINE_AK env var)')
    parser.add_argument('--sk', default=os.environ.get('VOLCENGINE_SK'),
                        help='Secret Key (or set VOLCENGINE_SK env var)')
    
    args = parser.parse_args()
    
    # Validate credentials
    if not args.ak or not args.sk:
        print("Error: Missing credentials. Please set VOLCENGINE_AK and VOLCENGINE_SK environment variables")
        print("       or provide them via --ak and --sk arguments.")
        sys.exit(1)
    
    try:
        generate_image(
            prompt=args.prompt,
            output_path=args.output,
            access_key=args.ak,
            secret_key=args.sk,
            width=args.width,
            height=args.height,
            seed=args.seed
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
