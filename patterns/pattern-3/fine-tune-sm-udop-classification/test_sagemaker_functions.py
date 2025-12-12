#!/usr/bin/env python3
"""
Test SageMaker inference functions locally before deployment
Simulates the SageMaker container environment
"""

import sys
import os
import json
import time
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent / "code"))


def setup_model_dir(checkpoint_path):
    """
    Create a temporary model directory that mimics SageMaker's /opt/ml/model
    """
    import tempfile
    import shutil
    
    tmpdir = tempfile.mkdtemp(prefix="sagemaker_model_")
    print(f"Created model directory: {tmpdir}")
    
    # Copy checkpoint if provided
    if checkpoint_path:
        checkpoint_path = os.path.abspath(checkpoint_path)
        if os.path.exists(checkpoint_path):
            dest = os.path.join(tmpdir, "best_model.ckpt")
            shutil.copy2(checkpoint_path, dest)
            print(f"  Copied checkpoint: {checkpoint_path}")
            print(f"  Destination: {dest}")
            print(f"  File exists: {os.path.exists(dest)}")
        else:
            print(f"  Warning: Checkpoint not found: {checkpoint_path}")
    
    # Create validation_prompt.json
    prompt_data = {"validation_prompt": "What is the document type?"}
    with open(os.path.join(tmpdir, "validation_prompt.json"), "w") as f:
        json.dump(prompt_data, f)
    print("  Created validation_prompt.json")
    
    return tmpdir


def test_inference_functions(inference_module, model_dir, test_image, test_textract):
    """
    Test the SageMaker inference functions: model_fn, input_fn, predict_fn, output_fn
    """
    print("\n" + "="*70)
    print("TESTING SAGEMAKER INFERENCE FUNCTIONS")
    print("="*70)
    
    # Test 1: model_fn
    print("\n--- Testing model_fn ---")
    start = time.time()
    try:
        model_artifacts = inference_module.model_fn(model_dir)
        load_time = time.time() - start
        print(f"✓ model_fn succeeded in {load_time:.2f}s")
        print(f"  Returned keys: {list(model_artifacts.keys())}")
    except Exception as e:
        print(f"✗ model_fn failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: input_fn
    print("\n--- Testing input_fn ---")
    
    # Create request body (JSON format)
    request_body = json.dumps({
        "input_image": test_image,
        "input_textract": test_textract,
        "prompt": None,
        "debug": False
    })
    
    start = time.time()
    try:
        parsed_input = inference_module.input_fn(request_body, "application/json")
        input_time = time.time() - start
        print(f"✓ input_fn succeeded in {input_time:.2f}s")
        print(f"  Parsed keys: {list(parsed_input.keys())}")
    except Exception as e:
        print(f"✗ input_fn failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: predict_fn
    print("\n--- Testing predict_fn ---")
    start = time.time()
    try:
        prediction = inference_module.predict_fn(parsed_input, model_artifacts)
        predict_time = time.time() - start
        print(f"✓ predict_fn succeeded in {predict_time:.2f}s")
        print(f"  Prediction: {prediction}")
    except Exception as e:
        print(f"✗ predict_fn failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: output_fn
    print("\n--- Testing output_fn ---")
    start = time.time()
    try:
        response = inference_module.output_fn(prediction, "application/json")
        output_time = time.time() - start
        print(f"✓ output_fn succeeded in {output_time:.2f}s")
        print(f"  Response: {response[:200]}...")
    except Exception as e:
        print(f"✗ output_fn failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Model loading: {load_time:.2f}s")
    print(f"Input parsing: {input_time:.2f}s")
    print(f"Prediction: {predict_time:.2f}s")
    print(f"Output formatting: {output_time:.2f}s")
    print(f"Total: {load_time + input_time + predict_time + output_time:.2f}s")
    print("\n✓ All SageMaker functions working correctly!")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test SageMaker inference functions locally"
    )
    parser.add_argument(
        "--inference-module",
        default="inference",
        help="Inference module to test (inference, inference_baseline, inference_optimized)"
    )
    parser.add_argument(
        "--checkpoint",
        help="Path to model checkpoint (optional, tests HF download if not provided)"
    )
    parser.add_argument(
        "--test-image",
        default="s3://idp-evaluation-datasets/datasets/udop-rvl_cdip/validation/images/0.png",
        help="S3 path to test image"
    )
    parser.add_argument(
        "--test-textract",
        default="s3://idp-evaluation-datasets/datasets/udop-rvl_cdip/validation/textract/0.json",
        help="S3 path to test textract JSON"
    )
    
    args = parser.parse_args()
    
    # Import the inference module
    print(f"Importing {args.inference_module}...")
    try:
        inference_module = __import__(args.inference_module)
        print(f"✓ Successfully imported {args.inference_module}")
    except Exception as e:
        print(f"✗ Failed to import {args.inference_module}: {e}")
        return 1
    
    # Setup model directory
    model_dir = setup_model_dir(args.checkpoint)
    
    try:
        # Run tests
        success = test_inference_functions(
            inference_module,
            model_dir,
            args.test_image,
            args.test_textract
        )
        
        return 0 if success else 1
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(model_dir, ignore_errors=True)
        print(f"\nCleaned up {model_dir}")


if __name__ == "__main__":
    sys.exit(main())
