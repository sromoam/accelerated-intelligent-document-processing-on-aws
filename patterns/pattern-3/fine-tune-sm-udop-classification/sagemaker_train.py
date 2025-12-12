#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import argparse
import json
import boto3
import sagemaker
from sagemaker.pytorch import PyTorch
from sagemaker.debugger import TensorBoardOutputConfig
from botocore.exceptions import ClientError

def create_sagemaker_role(role_name, bucket, data_bucket):
    """
    Create a least privilege IAM role for SageMaker training
    """
    iam = boto3.client('iam')
    
    # Define the role trust policy for SageMaker
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "sagemaker.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        # Create the IAM role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        # Attach AmazonSageMakerFullAccess managed policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
        )
        
        # Create custom policy for S3 access
        bucket_list = [bucket]
        if data_bucket and data_bucket != bucket:
            bucket_list.append(data_bucket)
            
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": sum([[f"arn:aws:s3:::{b}", f"arn:aws:s3:::{b}/*"] for b in bucket_list], [])
            }]
        }
        
        # Create and attach the custom policy
        policy_name = f"{role_name}-s3-access"
        iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(s3_policy)
        )
        
        account_id = boto3.client('sts').get_caller_identity()['Account']
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f'arn:aws:iam::{account_id}:policy/{policy_name}'
        )
        
        # Wait for role to be ready
        waiter = iam.get_waiter('role_exists')
        waiter.wait(RoleName=role_name)
        
        # Wait for policy attachments to propagate
        import time
        time.sleep(10)   # semgrep-ignore: arbitrary-sleep - Intentional delay. Duration is hardcoded and not user-controlled.
        
        return response['Role']['Arn']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            # If role exists, get its ARN
            response = iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        raise e

def create_training_job(role, bucket, job_name, bucket_prefix="", data_bucket="", 
                       data_bucket_prefix="", instance_type="ml.g5.12xlarge", 
                       hyperparameters=None):
    """
    Create and run a SageMaker training job
    """
    if not data_bucket:
        data_bucket = bucket
    if not data_bucket_prefix:
        data_bucket_prefix = bucket_prefix
        
    # If no role ARN provided, create one
    if not role:
        role_name = f"sagemaker-training-{job_name}"
        role = create_sagemaker_role(role_name, bucket, data_bucket)
        print(f"Created IAM role: {role}")
        
    # Helper function to construct S3 paths
    def get_s3_path(bucket_name, prefix, path):
        if prefix:
            return f"s3://{bucket_name}/{prefix.rstrip('/')}/{path}"
        return f"s3://{bucket_name}/{path}"
    
    sagemaker_session = sagemaker.Session()
    output_dir = '/opt/ml/output'
    
    # Update all S3 paths to include prefixes
    tensorboard_output_config = TensorBoardOutputConfig(
        s3_output_path=get_s3_path(bucket, bucket_prefix, "tensorboard"),
        container_local_output_path=output_dir + '/tensorboard'
    )
    
    # Add output_dir to hyperparameters (SageMaker-specific)
    if hyperparameters is None:
        hyperparameters = {}
    hyperparameters["output_dir"] = output_dir
    
    # Convert boolean enable_batching to string for SageMaker
    if "enable_batching" in hyperparameters and hyperparameters["enable_batching"]:
        hyperparameters["enable_batching"] = "true"
    elif "enable_batching" in hyperparameters:
        # Remove if False (don't pass the flag)
        del hyperparameters["enable_batching"]
    
    estimator = PyTorch(
        entry_point="train.py",
        source_dir="./code",
        role=role,
        framework_version="2.4.0",
        py_version="py311",
        instance_type=instance_type,
        instance_count=1,
        output_path=get_s3_path(bucket, bucket_prefix, "models/"),
        hyperparameters=hyperparameters,
        code_location=get_s3_path(bucket, bucket_prefix, "scripts/training/"),
        sagemaker_session=sagemaker_session,
        tensorboard_output_config=tensorboard_output_config,
        environment={"FI_EFA_FORK_SAFE": "1"}
    )
    
    # Update data channels with prefixed paths
    estimator.fit({
        "training": get_s3_path(data_bucket, data_bucket_prefix, "training"),
        "validation": get_s3_path(data_bucket, data_bucket_prefix, "validation")
    }, job_name=job_name)

    print(f"Model path: {get_s3_path(bucket, bucket_prefix, f'models/{job_name}/output/model.tar.gz')}")
    
    return sagemaker_session


if __name__ == "__main__":
    # Import hyperparameter parser from training_args
    import sys
    import os
    code_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code')
    sys.path.insert(0, code_dir)
    from training_args import get_hyperparameter_args_parser
    
    # Create parser with SageMaker-specific args + all hyperparameters
    parser = argparse.ArgumentParser(
        description='Launch UDOP training job on SageMaker',
        parents=[get_hyperparameter_args_parser()],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # SageMaker-specific arguments
    sagemaker_group = parser.add_argument_group(
        'SageMaker Configuration',
        'Arguments specific to SageMaker job configuration'
    )
    
    sagemaker_group.add_argument(
        "--role",
        type=str,
        required=False,
        default="",
        help="IAM Role ARN for SageMaker. If not provided, a role will be created automatically."
    )
    
    sagemaker_group.add_argument(
        "--bucket",
        type=str,
        required=True,
        help="S3 bucket name for training outputs (models, logs, tensorboard)"
    )
    
    sagemaker_group.add_argument(
        "--bucket-prefix",
        type=str,
        default="",
        help="Prefix for all outputs in the S3 bucket (e.g., 'experiments/run1')"
    )
    
    sagemaker_group.add_argument(
        "--job-name",
        type=str,
        required=True,
        help="Unique name for the SageMaker training job"
    )
    
    sagemaker_group.add_argument(
        "--data-bucket",
        type=str,
        default="",
        help="S3 bucket containing training data (defaults to --bucket if not specified)"
    )
    
    sagemaker_group.add_argument(
        "--data-bucket-prefix",
        type=str,
        default="",
        help="Prefix for training data in S3 (defaults to --bucket-prefix if not specified)"
    )
    
    sagemaker_group.add_argument(
        "--instance-type",
        type=str,
        default="ml.g5.12xlarge",
        help="SageMaker instance type (e.g., ml.g4dn.xlarge, ml.g4dn.12xlarge, ml.g5.12xlarge)"
    )
    
    args = parser.parse_args()
    
    # Build hyperparameters dict from all training args
    hyperparameters = {
        "max_epochs": args.max_epochs,
        "base_model": args.base_model,
        "lr": args.lr,
        "b1": args.b1,
        "b2": args.b2,
        "weight_decay": args.weight_decay,
        "lr_warmup_steps": args.lr_warmup_steps,
        "dropout_rate": args.dropout_rate,
        "accumulate_grad_batches": args.accumulate_grad_batches,
        "patience": args.patience,
        "precision": args.precision,
        "distributed_strategy": args.distributed_strategy,
        "print_every_n_steps": args.print_every_n_steps,
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "num_sanity_val_steps": args.num_sanity_val_steps,
    }
    
    # Add optional parameters
    if args.enable_batching:
        hyperparameters["enable_batching"] = True
    if args.fast_dev_run is not None:
        hyperparameters["fast_dev_run"] = args.fast_dev_run
    if args.max_steps is not None:
        hyperparameters["max_steps"] = args.max_steps
    
    create_training_job(
        role=args.role,
        bucket=args.bucket,
        job_name=args.job_name,
        bucket_prefix=args.bucket_prefix,
        data_bucket=args.data_bucket,
        data_bucket_prefix=args.data_bucket_prefix,
        instance_type=args.instance_type,
        hyperparameters=hyperparameters
    )