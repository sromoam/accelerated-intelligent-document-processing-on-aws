# UDOP Inference Throughput Benchmarking

## Overview

This guide covers benchmarking UDOP model inference on SageMaker endpoints, including latency testing, concurrent load testing, and accuracy validation.

## Prerequisites

### Required
- AWS credentials configured (`aws configure`)
- Python environment with dependencies installed
- Validation dataset: `data/udop_rvlcdip/` (for local testing)

### Optional (for fine-tuned model testing)
- Trained UDOP model checkpoint (`best_model.ckpt`)
- SageMaker execution role with S3 access

### Note on Model Requirements
**You need a trained checkpoint to deploy to SageMaker.** Vanilla HuggingFace weights cause timeouts because:
- Model download (3GB) takes 5+ minutes
- SageMaker container timeout is 60 seconds
- Download happens during first inference request, not at startup

For local testing only, vanilla weights work fine since there's no timeout.

## Step 1: Test Inference Functions Locally

### Option A: Test Vanilla Model (No Training Required)

Test the base UDOP model without any fine-tuning:

```bash
cd patterns/pattern-3/fine-tune-sm-udop-classification
conda activate udop

# Simple test
python test_vanilla_udop.py

# Or test using actual inference.py logic
python test_inference_vanilla.py
```

**Expected output**:
- Model loading: 5-10s
- Prediction: 1-2s on CPU
- Result: `{'prediction': 'letter'}` or similar document class

**What this tests**:
- ✓ Model loads from HuggingFace
- ✓ Inference code works
- ✓ S3 data loading works
- ✓ Prediction format is correct

### Option B: Test Fine-Tuned Model (Requires Checkpoint)

If you have a trained checkpoint:

```bash
conda activate udop

python test_sagemaker_functions.py \
  --inference-module inference \
  --checkpoint /path/to/best_model.ckpt
```

**Expected output**:
- Model loading: 8-20s (checkpoint is large)
- Prediction: 1-2s on CPU
- All functions should succeed

### Troubleshooting Step 1

**Issue**: `FileNotFoundError: data/udop_rvlcdip/`
- **Fix**: Download or sync the validation dataset first
- **Command**: `aws s3 sync s3://idp-evaluation-datasets/datasets/udop-rvl_cdip/validation/ data/udop_rvlcdip/validation/ --region us-west-2`

**Issue**: `ModuleNotFoundError: No module named 'transformers'`
- **Fix**: Install dependencies
- **Command**: `conda activate udop && pip install -r code/requirements.txt`

**Issue**: Model loading takes >30s
- **Expected**: First time downloads model from HuggingFace (~3GB), subsequent loads are cached
- **Location**: `~/.cache/huggingface/`

## Step 2: Package Model for Deployment

Create a model.tar.gz containing the checkpoint and inference code:

```bash
python package_model.py \
  --checkpoint /path/to/best_model.ckpt \
  --output baseline_model.tar.gz
```

For optimized inference (max_new_tokens=4, num_beams=1, torch.no_grad):

```bash
python package_model.py \
  --checkpoint /path/to/best_model.ckpt \
  --output optimized_model.tar.gz \
  --optimized
```

The script packages:
- Model checkpoint (8-9GB)
- Inference code (inference.py or inference_optimized.py)
- Dependencies (model.py, utils.py, model_versions.py)
- validation_prompt.json with correct prompt

Output: ~3-4GB compressed tar.gz (takes 4-5 minutes)

## Step 3: Deploy to SageMaker

Upload model artifact:

```bash
aws s3 cp baseline_model.tar.gz s3://YOUR-BUCKET/models/ --region us-west-2
```

Deploy endpoint:

```bash
export AWS_DEFAULT_REGION=us-west-2

python sagemaker_deploy.py \
  --model-artifact s3://YOUR-BUCKET/models/baseline_model.tar.gz \
  --endpoint-name udop-baseline-$(date +%s) \
  --role arn:aws:iam::ACCOUNT:role/SageMakerExecutionRole
```

Deployment takes 5-10 minutes. The endpoint will be on ml.g4dn.2xlarge by default.

## Step 4: Run Benchmarks

### Basic Sequential Test

```bash
python benchmark_inference.py \
  --endpoint-name udop-baseline-TIMESTAMP \
  --local-data data/udop_rvlcdip \
  --region us-west-2 \
  --num-samples 5 \
  --iterations 5 \
  --output baseline_benchmark.json
```

Measures:
- Warmup latency (first 3 requests)
- Steady-state latency statistics
- Throughput (requests/second)

### Advanced Concurrent Testing

```bash
python benchmark_advanced.py \
  --endpoint-name udop-baseline-TIMESTAMP \
  --region us-west-2 \
  --all \
  --num-samples 25 \
  --throughput-samples 1000 \
  --throughput-concurrency 20 \
  --output advanced_benchmark.json
```

Tests:
- Sequential (1 request at a time)
- Concurrent (5, 10, 20 parallel requests)
- Throughput (1000 documents with 20 workers)
- Accuracy scoring against ground truth labels

## Expected Results

### Baseline (inference.py)
- **Latency**: 400-500ms per document on T4 GPU
- **Throughput**: 2-3 requests/second (sequential)
- **Accuracy**: Should match training validation accuracy

### Optimized (inference_optimized.py)
- **Latency**: Similar to baseline without torch.compile()
- **With torch.compile()**: 20-40% faster (300-400ms)
- **Throughput**: Scales with concurrency up to GPU saturation

## Common Issues

### Issue: Endpoint times out on first request
**Cause**: Trying to download vanilla HF weights (3GB) during inference
**Solution**: Always deploy with a packaged checkpoint - vanilla weights don't work on SageMaker due to 60s timeout

### Issue: 0% accuracy
**Cause**: Wrong prompt - model trained with "Document Classification on RVLCDIP." but inference uses different prompt
**Solution**: Ensure validation_prompt.json matches training prompt, or pass correct prompt in requests

### Issue: GPU utilization shows 0% in CloudWatch
**Cause**: CloudWatch samples every 1-5 minutes, misses brief GPU spikes
**Reality**: If latency is 400-500ms, GPU is being used. CPU would be 5-10 seconds.

### Issue: ValueError: Exactly one .pth or .pt file required
**Cause**: Deployed with `model_data=None` and no checkpoint
**Solution**: Package checkpoint into model.tar.gz - vanilla deployment doesn't work on SageMaker

### Issue: Slow packaging (4+ minutes)
**Cause**: Compressing 8-9GB checkpoint
**Expected**: Normal, tar.gz compression takes time

## Cleanup

Delete endpoints when done:

```bash
aws sagemaker delete-endpoint --endpoint-name udop-baseline-TIMESTAMP --region us-west-2
aws sagemaker delete-endpoint --endpoint-name udop-optimized-TIMESTAMP --region us-west-2
```

## Files Created

- `package_model.py` - Package checkpoints for deployment
- `test_sagemaker_functions.py` - Test inference locally before deploying
- `test_single_prediction.py` - Test individual predictions
- `benchmark_inference.py` - Basic sequential benchmarking
- `benchmark_advanced.py` - Concurrent load testing with accuracy
- `test_local_inference.py` - Compare baseline vs optimized locally

## Key Learnings

1. **Always use trained checkpoints** - Downloading from HuggingFace during inference causes timeouts
2. **Prompt matters** - Model must receive the exact prompt it was trained with
3. **GPU metrics are misleading** - CloudWatch can't capture brief inference spikes
4. **Test locally first** - Catch issues before deploying (saves time and money)
5. **Packaging takes time** - 8GB checkpoint compression is slow but necessary
