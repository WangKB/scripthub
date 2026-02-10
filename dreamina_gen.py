#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import hmac
import argparse
from datetime import datetime, timezone
import urllib.request

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(secret_key, date_stamp, region_name, service_name):
    # kDate = HMAC-SHA256(SecretKey, date_stamp) - NOT using "VCT" prefix for this attempt
    k_date = sign(secret_key.encode("utf-8"), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, "request")
    return k_signing

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompt', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()

    ak = os.environ.get('VOLCENGINE_AK')
    sk = os.environ.get('VOLCENGINE_SK')

    method = 'POST'
    service = 'cv'
    region = 'cn-north-1'
    host = 'open.volcengineapi.com'
    content_type = 'application/json'
    version = '2022-08-31'
    action = 'CVProcess'

    body_dict = {
        "req_key": "high_aes_general_v21_L",
        "prompt": args.prompt,
        "width": 1024,
        "height": 1024,
        "return_url": True,
        "logo_info": {"add_logo": False}
    }
    body = json.dumps(body_dict, separators=(',', ':')).encode('utf-8')
    payload_hash = hashlib.sha256(body).hexdigest()

    now = datetime.now(timezone.utc)
    x_date = now.strftime('%Y%m%dT%H%M%SZ')
    short_date = now.strftime('%Y%m%d')

    query = f"Action={action}&Version={version}"
    headers_for_sig = {
        "content-type": content_type,
        "host": host,
        "x-content-sha256": payload_hash,
        "x-date": x_date
    }
    
    sorted_keys = sorted(headers_for_sig.keys())
    signed_headers = ";".join(sorted_keys)
    canonical_headers = "".join([f"{k}:{headers_for_sig[k]}\n" for k in sorted_keys])
    canonical_request = f"{method}\n/\n{query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    
    algorithm = 'VCT-HMAC-SHA256'
    credential_scope = f"{short_date}/{region}/{service}/request"
    string_to_sign = f"{algorithm}\n{x_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    signing_key = get_signature_key(sk, short_date, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization = f"{algorithm} Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    final_headers = {
        "Content-Type": content_type,
        "X-Content-Sha256": payload_hash,
        "X-Date": x_date,
        "Authorization": authorization
    }

    url = f"https://{host}/?{query}"
    req = urllib.request.Request(url, data=body, headers=final_headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            if "data" in res and "image_url" in res["data"]:
                urllib.request.urlretrieve(res['data']['image_url'], args.output)
                print(f"Success: {args.output}")
            else:
                print(json.dumps(res, indent=2))
    except Exception as e:
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))
        else:
            print(f"Failed: {e}")

if __name__ == '__main__':
    main()
