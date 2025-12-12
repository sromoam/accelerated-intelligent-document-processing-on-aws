#!/usr/bin/env python3
"""Test a single prediction to see what the model outputs"""

import boto3
import json
import sagemaker
from pathlib import Path

def test_prediction(endpoint_name, data_dir, sample_id="0", region="us-west-2"):
    runtime = boto3.client('sagemaker-runtime', region_name=region)
    s3 = boto3.client('s3', region_name=region)
    
    # Load sample
    image_file = f"{data_dir}/validation/images/{sample_id}.png"
    textract_file = f"{data_dir}/validation/textract/{sample_id}.json"
    label_file = f"{data_dir}/validation/labels/{sample_id}.json"
    
    # Get true label
    with open(label_file) as f:
        true_label = json.load(f)['label']
    
    print(f"Testing sample {sample_id}")
    print(f"True label: {true_label}")
    
    # Upload to S3
    boto_session = boto3.Session(region_name=region)
    sm_session = sagemaker.Session(boto_session=boto_session)
    bucket = sm_session.default_bucket()
    prefix = f"test-single/{endpoint_name}"
    
    image_key = f"{prefix}/test_image.png"
    textract_key = f"{prefix}/test_textract.json"
    
    s3.upload_file(image_file, bucket, image_key)
    s3.upload_file(textract_file, bucket, textract_key)
    
    # Invoke endpoint
    payload = {
        'input_image': f"s3://{bucket}/{image_key}",
        'input_textract': f"s3://{bucket}/{textract_key}",
        'prompt': None,
        'debug': True  # Get debug info
    }
    
    print(f"\nInvoking endpoint...")
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    result = json.loads(response['Body'].read().decode())
    
    print(f"\nResponse:")
    print(json.dumps(result, indent=2))
    
    prediction = result.get('prediction', '').strip()
    print(f"\nPrediction: '{prediction}'")
    print(f"True label: '{true_label}'")
    print(f"Match: {prediction.lower() == true_label.lower()}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint-name", required=True)
    parser.add_argument("--data-dir", default="data/udop_rvlcdip")
    parser.add_argument("--sample-id", default="0")
    parser.add_argument("--region", default="us-west-2")
    args = parser.parse_args()
    
    test_prediction(args.endpoint_name, args.data_dir, args.sample_id, args.region)
