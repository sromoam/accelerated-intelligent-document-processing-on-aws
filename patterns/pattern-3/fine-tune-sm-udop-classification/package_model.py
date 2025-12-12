#!/usr/bin/env python3
"""
Package a trained model checkpoint for SageMaker deployment
"""

import tarfile
import shutil
import json
import os
import argparse
from pathlib import Path


def package_model(checkpoint_path, output_path="model.tar.gz", use_optimized=False):
    """
    Package model checkpoint with inference code into model.tar.gz
    """
    print(f"Packaging model from {checkpoint_path}...")
    
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    # Create temporary directory structure
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Copy checkpoint
        print("  Copying checkpoint...")
        shutil.copy2(checkpoint_path, tmpdir / "best_model.ckpt")
        
        # Copy inference code
        print("  Copying inference code...")
        code_dir = tmpdir / "code"
        code_dir.mkdir()
        
        inference_file = "inference_optimized.py" if use_optimized else "inference.py"
        source_file = "inference_optimized.py" if use_optimized else "inference.py"
        
        files_to_copy = [
            (f"code/{source_file}", code_dir / "inference.py"),
            ("code/model.py", code_dir / "model.py"),
            ("code/utils.py", code_dir / "utils.py"),
            ("code/model_versions.py", code_dir / "model_versions.py"),
            ("code/requirements.txt", code_dir / "requirements.txt"),
        ]
        
        for src, dst in files_to_copy:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"    Copied {src}")
        
        # Create validation_prompt.json
        print("  Creating validation_prompt.json...")
        prompt_data = {"validation_prompt": "What is the document type?"}
        with open(tmpdir / "validation_prompt.json", "w") as f:
            json.dump(prompt_data, f)
        
        # Create tarball
        print(f"  Creating {output_path}...")
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(tmpdir, arcname=".")
        
        # Get size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n✓ Created {output_path} ({size_mb:.1f} MB)")
        
        return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Package trained model for SageMaker deployment"
    )
    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to model checkpoint (.ckpt file)"
    )
    parser.add_argument(
        "--output",
        default="model.tar.gz",
        help="Output path for model.tar.gz"
    )
    parser.add_argument(
        "--optimized",
        action="store_true",
        help="Use optimized inference code"
    )
    
    args = parser.parse_args()
    
    package_model(args.checkpoint, args.output, args.optimized)
    
    print("\nNext steps:")
    print("1. Upload to S3:")
    print(f"   aws s3 cp {args.output} s3://YOUR-BUCKET/models/")
    print("\n2. Deploy:")
    print("   python sagemaker_deploy.py \\")
    print("     --model-artifact s3://YOUR-BUCKET/models/model.tar.gz \\")
    print("     --endpoint-name udop-baseline-$(date +%s) \\")
    print("     --role arn:aws:iam::195275636621:role/AmazonSageMakerExecutionRole-builder-Sagemaker")
