# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import time
_script_start = time.time()
print(f"[{time.time() - _script_start:.2f}s] Script started")

import argparse
print(f"[{time.time() - _script_start:.2f}s] argparse imported")
import json
import os
import shutil
import torch

print(f"[{time.time() - _script_start:.2f}s] Importing lightning...")
import lightning.pytorch as pl
print(f"[{time.time() - _script_start:.2f}s] Importing numpy...")
import numpy as np

print(f"[{time.time() - _script_start:.2f}s] Importing callbacks...")
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.callbacks.early_stopping import EarlyStopping
from lightning.pytorch.loggers import TensorBoardLogger 
from torch.utils.data import DataLoader
from transformers import AutoProcessor

print(f"[{time.time() - _script_start:.2f}s] Importing model and utils...")
from model import UDOPModel
from utils import ClassificationDataset

# Import for secure model version management
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_versions import get_model_revision
print(f"[{time.time() - _script_start:.2f}s] All imports complete")


def train(
    data_dir, model_dir, script_dir, output_dir, max_epochs, accumulate_grad_batches, 
    devices, base_model, lr, lr_warmup_steps, dropout_rate, b1, b2, weight_decay,
    print_every_n_steps, patience, fast_dev_run, precision, distributed_strategy, num_workers,
    batch_size, enable_batching, num_sanity_val_steps, max_steps, max_train_samples, max_val_samples,
    verbose
):
    import time
    start_time = time.time()
    
    def log_timing(step):
        elapsed = time.time() - start_time
        print(f"[{elapsed:.2f}s] {step}")
    
    log_timing("START train()")
    
    shutil.copytree(script_dir, os.path.join(model_dir, "code"), dirs_exist_ok=True)
    log_timing("Copied script_dir to model_dir")
    
    tb_logger = TensorBoardLogger(
        save_dir=os.path.join(output_dir, "tensorboard"),
        name="training_logs"
    )
    log_timing("Created TensorBoard logger")
    # Load processor with pinned revision for security (addresses B615 finding)
    log_timing("Loading processor...")
    revision = get_model_revision(base_model) if base_model in ["microsoft/udop-large"] else None
    if revision:
        print(f"Loading processor for {base_model} with pinned revision: {revision}")
        processor = AutoProcessor.from_pretrained(base_model, revision=revision, apply_ocr=False)
    else:
        # nosec B615 - Sample training code for demonstration purposes
        # This fallback path is only for custom models during development/testing
        # Production deployments should use pinned revisions from model_versions.py
        print(f"Loading processor for {base_model} without revision pinning (not in managed list)")
        processor = AutoProcessor.from_pretrained(base_model, apply_ocr=False)
    log_timing("Processor loaded")
    
    log_timing("Creating datasets...")
    train_ds = ClassificationDataset(processor, data_dir, split="training", enable_batching=enable_batching, max_samples=max_train_samples)
    val_ds = ClassificationDataset(processor, data_dir, split="validation", enable_batching=enable_batching, max_samples=max_val_samples)
    log_timing(f"Datasets created (train={len(train_ds)}, val={len(val_ds)})")

    assert train_ds.prompt.strip() == val_ds.prompt.strip(), ( # nosec B101
        "Prompts do not match in training and validation dataset!\nTraining Prompt: {0}\nValidation Prompt: {1}".format(
            train_ds.prompt, val_ds.prompt
        )
    )
    
    log_timing("Creating dataloaders...")
    # nosemgrep: trailofbits.python.automatic-memory-pinning.automatic-memory-pinning - pin_memory is a performance optimization; default behavior is safe and functional
    if enable_batching:
        # Use custom collate for batching - handles metadata alongside tensors
        from utils import collate_batch_with_metadata
        train_dl = DataLoader(
            train_ds, batch_size=batch_size, num_workers=num_workers,
            collate_fn=collate_batch_with_metadata,
            shuffle=True
        )
        val_dl = DataLoader(
            val_ds, batch_size=batch_size, num_workers=num_workers,
            collate_fn=collate_batch_with_metadata,
            shuffle=False  # Don't shuffle validation
        )
    else:
        # Original implementation - batch_size=1 with custom collate
        train_dl = DataLoader(
            train_ds, batch_size=1, num_workers=num_workers,
            collate_fn=lambda x: x[0], shuffle=True
        )
        val_dl = DataLoader(
            val_ds, batch_size=1, num_workers=num_workers, 
            collate_fn=lambda x: x[0], shuffle=True
        )

    log_timing("Dataloaders created")
    
    max_steps = (
        (max_epochs * len(train_ds)) // accumulate_grad_batches // devices
    )

    log_timing("Creating model...")
    model = UDOPModel(
        model_id=base_model,
        lr=lr, lr_warmup_steps=lr_warmup_steps,
        dropout_rate=dropout_rate, max_steps=max_steps,
        b1=b1, b2=b2, weight_decay=weight_decay,
        print_every_n_steps=print_every_n_steps
    )

    log_timing("Model created")
    
    log_timing("Setting up callbacks...")
    callbacks = []
    callbacks.append(ModelCheckpoint(
        monitor="val_weighted_avg_f1", mode="max", save_top_k=1,
        filename='best_model', dirpath=model_dir,  verbose=True
    ))
    callbacks.append(EarlyStopping(
        monitor="val_weighted_avg_f1", mode="max", patience=patience,
    ))

    log_timing("Callbacks configured")
    
    log_timing("Creating Trainer...")
    # Determine accelerator based on strategy and available hardware
    if distributed_strategy == "auto":
        # Auto mode: Use GPU if available, otherwise CPU
        if torch.cuda.is_available():
            accelerator = "auto"
            distributed_strategy = "auto"  # Let Lightning choose best strategy
            print("Using GPU with auto strategy")
        else:
            accelerator = "cpu"
            print("Using CPU accelerator (no GPU available or MPS compatibility issues)")
    else:
        # Explicit strategy provided - use GPU
        accelerator = "gpu"
        print(f"Using GPU with strategy: {distributed_strategy}")
    
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        max_steps=max_steps if max_steps else -1,  # -1 means no limit
        log_every_n_steps=1,
        accelerator=accelerator,
        fast_dev_run=fast_dev_run,
        devices=devices,
        callbacks=callbacks,
        accumulate_grad_batches=accumulate_grad_batches,
        logger=tb_logger if verbose else False,
        precision=precision,
        strategy=distributed_strategy,
        num_sanity_val_steps=num_sanity_val_steps,
        enable_progress_bar=verbose,
        enable_model_summary=verbose
    )
    log_timing("Trainer created")
    
    log_timing("Calling trainer.fit() - THIS IS WHERE DELAY HAPPENS")
    trainer.fit(model, train_dataloaders=train_dl, val_dataloaders=val_dl)
    log_timing("Training complete")
    metrics = trainer.callback_metrics
    final_metrics = {k: v.item() for k, v in metrics.items()}

    metrics_dir = os.path.join(output_dir, "data")
    os.makedirs(metrics_dir, exist_ok=True)
    metrics_filename = os.path.join(metrics_dir, "training_metrics.json")
    with open(metrics_filename, "w") as f:
        json.dump(final_metrics, f)

    prompt_filename = os.path.join(model_dir, "validation_prompt.json")
    with open(prompt_filename, "w") as f:
        json.dump({"validation_prompt": train_ds.prompt}, f)


if __name__ == "__main__":
    print(f"[{time.time() - _script_start:.2f}s] Importing training_args...")
    from training_args import get_all_training_args_parser
    
    print(f"[{time.time() - _script_start:.2f}s] Creating argument parser...")
    parser = get_all_training_args_parser()
    print(f"[{time.time() - _script_start:.2f}s] Parsing arguments...")
    args = parser.parse_args()
    print(f"[{time.time() - _script_start:.2f}s] Arguments parsed, calling train()")
    train(
        args.data_dir, args.model_dir, args.script_dir, args.output_dir, 
        args.max_epochs, args.accumulate_grad_batches, args.devices, 
        args.base_model, args.lr, args.lr_warmup_steps, args.dropout_rate, 
        args.b1, args.b2, args.weight_decay, args.print_every_n_steps, 
        args.patience, args.fast_dev_run, args.precision, args.distributed_strategy, args.num_workers,
        args.batch_size, args.enable_batching, args.num_sanity_val_steps, args.max_steps,
        args.max_train_samples, args.max_val_samples, args.verbose
    )
