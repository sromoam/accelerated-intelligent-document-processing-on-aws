#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Deploy baseline UDOP model with default HuggingFace weights for benchmarking.
Uses source_dir to avoid creating tar.gz manually.
"""

import argparse
import sagemaker
from sagemaker.pytorch import PyTorchModel
import os


def create_model_artifact(base_model="microsoft/udop-large"):
    """Create model.tar.gz with inference code"""
    import tarfile
    import tempfile
    import shutil
    import json
    
    print("Creating model artifact...")
    with tempfile.TemporaryDirectory() as tmpdir:
        code_dir = os.path.join(tmpdir, "code")
        os.makedirs(code_dir)
        
        # Copy inference files
        for f in ["inference_baseline.py", "utils.py", "model.py", "model_versions.py", "requirements.txt"]:
            src = os.path.join("code", f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(code_dir, f))
        
        # Rename to inference.py
        shutil.move(
            os.path.join(code_dir, "inference_baseline.py"),
            os.path.join(code_dir, "inference.py")
        )
        
        # Create validation_prompt.json
        with open(os.path.join(tmpdir, "validation_prompt.json"), "w") as f:
            json.dump({"validation_prompt": "What is the document type?"}, f)
        
        # Create tar.gz
        artifact_path = "model.tar.gz"
        with tarfile.open(artifact_path, "w:gz") as tar:
            tar.add(tmpdir, arcname=".")
        
        print(f"Created {artifact_path}")
        return artifact_path


def deploy_baseline_model(
    endpoint_name,
    role=None,
    instance_type="ml.g4dn.xlarge",
    base_model="microsoft/udop-large",
    region="us-west-2"
):
    """
    Deploy baseline model to SageMaker endpoint.
    Model weights will be downloaded from HuggingFace during deployment.
    """
    print(f"\nDeploying baseline model to endpoint: {endpoint_name}")
    print(f"  Instance type: {instance_type}")
    print(f"  Base model: {base_model}")
    print(f"  Region: {region}")
    
    import boto3
    boto_session = boto3.Session(region_name=region)
    sagemaker_session = sagemaker.Session(boto_session=boto_session)
    
    # Create and upload model artifact
    artifact_path = create_model_artifact(base_model)
    bucket = sagemaker_session.default_bucket()
    prefix = f"baseline-models/{endpoint_name}"
    model_data = sagemaker_session.upload_data(artifact_path, bucket, prefix)
    os.remove(artifact_path)
    print(f"Uploaded model to: {model_data}")
    
    # Use provided role or try to get execution role
    if not role:
        try:
            role = sagemaker.get_execution_role()
        except Exception as e:
            print(f"\nError: Could not determine execution role.")
            print(f"Please provide a role ARN with --role parameter")
            print(f"\nThe role must have:")
            print(f"  1. Trust policy allowing sagemaker.amazonaws.com")
            print(f"  2. AmazonSageMakerFullAccess policy")
            raise e
    
    print(f"  Using role: {role}")
    
    pytorch_model = PyTorchModel(
        model_data=model_data,
        role=role,
        framework_version="2.4.0",
        py_version="py311",
        entry_point="inference.py",
        sagemaker_session=sagemaker_session,
        env={
            "BASE_MODEL": base_model,
            "MMS_DEFAULT_RESPONSE_TIMEOUT": "900",
            "MODEL_SERVER_TIMEOUT": "900",
            "SAGEMAKER_MODEL_SERVER_TIMEOUT": "900"
        }
    )
    
    print("\nDeploying endpoint (this may take 5-10 minutes)...")
    print("Note: First deployment will download ~3GB model from HuggingFace")
    
    predictor = pytorch_model.deploy(
        initial_instance_count=1,
        instance_type=instance_type,
        endpoint_name=endpoint_name,
        wait=True
    )
    
    print(f"\n✓ Endpoint deployed successfully: {endpoint_name}")
    return predictor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy baseline UDOP model for benchmarking"
    )
    parser.add_argument(
        "--endpoint-name",
        type=str,
        required=True,
        help="Name for the SageMaker endpoint"
    )
    parser.add_argument(
        "--instance-type",
        type=str,
        default="ml.g4dn.xlarge",
        help="SageMaker instance type (default: ml.g4dn.xlarge)"
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="microsoft/udop-large",
        help="HuggingFace model ID"
    )
    parser.add_argument(
        "--role",
        type=str,
        default=None,
        help="IAM role ARN for SageMaker (must trust sagemaker.amazonaws.com)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-west-2",
        help="AWS region (default: us-west-2)"
    )
    
    args = parser.parse_args()
    
    # Deploy endpoint
    predictor = deploy_baseline_model(
        endpoint_name=args.endpoint_name,
        role=args.role,
        instance_type=args.instance_type,
        base_model=args.base_model,
        region=args.region
    )
    
    print("\n" + "="*60)
    print("DEPLOYMENT COMPLETE")
    print("="*60)
    print(f"Endpoint name: {args.endpoint_name}")
    print(f"Instance type: {args.instance_type}")
    print(f"Base model: {args.base_model}")
    print("\nNext steps:")
    print(f"  1. Test endpoint: python benchmark_inference.py --endpoint-name {args.endpoint_name}")
    print(f"  2. Delete endpoint: aws sagemaker delete-endpoint --endpoint-name {args.endpoint_name}")
