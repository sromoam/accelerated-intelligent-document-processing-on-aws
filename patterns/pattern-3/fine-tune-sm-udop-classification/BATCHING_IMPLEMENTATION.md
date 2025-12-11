# Batching Implementation for UDOP Training

## Overview

Implemented support for `batch_size > 1` in UDOP training by adding padding and custom collation.

## Changes Made

### 1. `code/utils.py`
- Added `enable_batching` parameter to `ClassificationDataset`
- When `enable_batching=True`:
  - Pads sequences to `max_length` (default 1024)
  - Squeezes batch dimension from processor output
  - Returns individual tensors instead of nested dict
- Added `collate_batch_with_metadata()` function to handle batching with non-tensor metadata (evaluator, task, labels)

### 2. `code/train.py`
- Added `--batch_size` and `--enable_batching` arguments
- Conditional DataLoader creation:
  - `enable_batching=True`: Uses custom collate, supports batch_size > 1
  - `enable_batching=False`: Original implementation with batch_size=1

### 3. `code/model.py`
- Updated `generic_step()` to handle both data formats:
  - Old format: `batch['model_inputs']` dict
  - New format: Direct tensor keys
- Fixed decoding logic to handle batched predictions
- Updated epoch end methods to flatten lists properly

## Usage

### Batch Size = 1 (Original)
```bash
python code/train.py \
  --data_dir data/udop_rvlcdip \
  --batch_size 1
  # enable_batching defaults to False
```

### Batch Size > 1 (New)
```bash
python code/train.py \
  --data_dir data/udop_rvlcdip \
  --batch_size 4 \
  --enable_batching
```

## Testing

Quick test with batch_size=2:
```bash
./test_batching.sh
```

Or manually:
```bash
conda run -n udop python code/train.py \
  --data_dir data/udop_rvlcdip \
  --model_dir output/test \
  --output_dir output/test \
  --fast_dev_run 2 \
  --batch_size 2 \
  --enable_batching \
  --num_workers 0 \
  --distributed_strategy auto
```

## Performance Tradeoffs

**Batch Size = 1 (No Padding)**
- ✓ Memory efficient
- ✓ No wasted computation on padding
- ✗ Slower (more forward passes)

**Batch Size > 1 (With Padding)**
- ✓ Faster training (fewer forward passes)
- ✗ Memory intensive (all sequences padded to max_length=1024)
- ✗ Wasted computation on padding tokens

## Acceptance Criteria

✅ Forward and backward pass work with batch_size > 1
✅ Backward compatible with original batch_size=1 implementation
✅ Metrics computed correctly for batched predictions
