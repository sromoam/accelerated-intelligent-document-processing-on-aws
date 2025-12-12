#!/usr/bin/env python3
"""
Test inference locally to benchmark baseline vs optimized performance
"""

import time
import json
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent / "code"))

from model import UDOPModel
from utils import InferenceHelper
from transformers import AutoProcessor
from model_versions import get_model_revision


def load_model(checkpoint_path, model_id="microsoft/udop-large"):
    """Load model from checkpoint"""
    print(f"Loading model from {checkpoint_path}...")
    start = time.time()
    
    model = UDOPModel.load_from_checkpoint(
        checkpoint_path=checkpoint_path,
        model_id=model_id
    )
    model.eval()
    
    # Load processor
    revision = get_model_revision(model_id)
    processor = AutoProcessor.from_pretrained(
        model_id, 
        revision=revision, 
        apply_ocr=False
    )
    
    load_time = time.time() - start
    print(f"Model loaded in {load_time:.2f}s")
    
    return model, processor


def run_inference(model, processor, image_path, textract_path, prompt="What is the document type?", optimized=False):
    """Run inference on a single document"""
    import torch
    from PIL import Image
    
    # Load inputs
    with open(textract_path) as f:
        textract = json.load(f)
    image = Image.open(image_path)
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Prepare inputs
    ih = InferenceHelper()
    inputs = ih.prepare_model_input(processor, image, textract, prompt)
    
    # Move to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    for key in inputs:
        if isinstance(inputs[key], torch.Tensor):
            inputs[key] = inputs[key].to(device)
    
    # Run inference
    start = time.time()
    
    if optimized:
        # Optimized generation parameters
        with torch.no_grad():
            outputs = model.model.generate(
                **inputs,
                max_new_tokens=4,
                num_beams=1,
                do_sample=False,
                early_stopping=True,
                use_cache=True
            )
    else:
        # Baseline generation (default parameters)
        outputs = model.model.generate(**inputs)
    
    latency = time.time() - start
    
    # Decode
    prediction = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    
    return prediction, latency


def benchmark(checkpoint_path, data_dir, num_samples=5, num_iterations=3):
    """Benchmark baseline vs optimized inference"""
    import glob
    
    print("="*70)
    print("LOCAL INFERENCE BENCHMARK")
    print("="*70)
    
    # Load model once
    model, processor = load_model(checkpoint_path)
    
    # Get test samples
    textract_files = glob.glob(f"{data_dir}/validation/textract/*.json")[:num_samples]
    
    if not textract_files:
        print(f"No test files found in {data_dir}/validation/textract/")
        return
    
    print(f"\nFound {len(textract_files)} test samples")
    print(f"Running {num_iterations} iterations per sample\n")
    
    # Prepare test data
    test_samples = []
    for textract_file in textract_files:
        base_name = Path(textract_file).stem
        image_file = f"{data_dir}/validation/images/{base_name}.png"
        if os.path.exists(image_file):
            test_samples.append((image_file, textract_file))
    
    # Warmup
    print("Warming up...")
    if test_samples:
        _, _ = run_inference(model, processor, *test_samples[0], optimized=False)
        print("Warmup complete\n")
    
    # Benchmark baseline
    print("--- BASELINE INFERENCE ---")
    baseline_latencies = []
    for i, (img, txt) in enumerate(test_samples):
        print(f"Sample {i+1}/{len(test_samples)}")
        for j in range(num_iterations):
            pred, lat = run_inference(model, processor, img, txt, optimized=False)
            baseline_latencies.append(lat)
            print(f"  Iteration {j+1}: {lat:.3f}s - {pred}")
    
    # Benchmark optimized
    print("\n--- OPTIMIZED INFERENCE ---")
    optimized_latencies = []
    for i, (img, txt) in enumerate(test_samples):
        print(f"Sample {i+1}/{len(test_samples)}")
        for j in range(num_iterations):
            pred, lat = run_inference(model, processor, img, txt, optimized=True)
            optimized_latencies.append(lat)
            print(f"  Iteration {j+1}: {lat:.3f}s - {pred}")
    
    # Results
    import numpy as np
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print("\nBaseline:")
    print(f"  Mean: {np.mean(baseline_latencies):.3f}s")
    print(f"  Median: {np.median(baseline_latencies):.3f}s")
    print(f"  Min: {np.min(baseline_latencies):.3f}s")
    print(f"  Max: {np.max(baseline_latencies):.3f}s")
    print(f"  P95: {np.percentile(baseline_latencies, 95):.3f}s")
    
    print("\nOptimized:")
    print(f"  Mean: {np.mean(optimized_latencies):.3f}s")
    print(f"  Median: {np.median(optimized_latencies):.3f}s")
    print(f"  Min: {np.min(optimized_latencies):.3f}s")
    print(f"  Max: {np.max(optimized_latencies):.3f}s")
    print(f"  P95: {np.percentile(optimized_latencies, 95):.3f}s")
    
    speedup = np.mean(baseline_latencies) / np.mean(optimized_latencies)
    print(f"\nSpeedup: {speedup:.2f}x")
    
    # Save report
    report = {
        "checkpoint": checkpoint_path,
        "num_samples": len(test_samples),
        "iterations_per_sample": num_iterations,
        "baseline": {
            "mean": float(np.mean(baseline_latencies)),
            "median": float(np.median(baseline_latencies)),
            "min": float(np.min(baseline_latencies)),
            "max": float(np.max(baseline_latencies)),
            "p95": float(np.percentile(baseline_latencies, 95)),
            "latencies": [float(x) for x in baseline_latencies]
        },
        "optimized": {
            "mean": float(np.mean(optimized_latencies)),
            "median": float(np.median(optimized_latencies)),
            "min": float(np.min(optimized_latencies)),
            "max": float(np.max(optimized_latencies)),
            "p95": float(np.percentile(optimized_latencies, 95)),
            "latencies": [float(x) for x in optimized_latencies]
        },
        "speedup": float(speedup)
    }
    
    output_file = "local_inference_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint")
    parser.add_argument("--data-dir", default="data/udop_rvlcdip", help="Data directory")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of test samples")
    parser.add_argument("--num-iterations", type=int, default=3, help="Iterations per sample")
    
    args = parser.parse_args()
    
    benchmark(args.checkpoint, args.data_dir, args.num_samples, args.num_iterations)
