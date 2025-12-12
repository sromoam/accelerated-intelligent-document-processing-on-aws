# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
PyTorch Lightning module for UDOP (Unified Document Processing) model fine-tuning.

This module provides a Lightning wrapper around the UDOP model for document
classification tasks. It supports both single-sample and batched training modes,
with automatic handling of variable-length sequences.

Key Features:
    - Secure model loading with pinned revisions
    - Dual-mode support: batch_size=1 (original) and batch_size>1 (batched)
    - Cosine learning rate schedule with warmup
    - Automatic metric computation and logging
    - Memory usage tracking
"""

import torch

import lightning.pytorch as pl

from transformers import UdopForConditionalGeneration
from transformers.optimization import get_cosine_schedule_with_warmup

# Import for secure model version management
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_versions import get_model_revision


class UDOPModel(pl.LightningModule):
    """
    PyTorch Lightning module for UDOP document classification.
    
    This class wraps the UDOP model for conditional generation and provides
    training, validation, and prediction functionality. It handles both
    single-sample (batch_size=1) and batched (batch_size>1) training modes.
    
    The model uses:
        - Adam optimizer with configurable betas and weight decay
        - Cosine learning rate schedule with warmup
        - Automatic mixed precision training support
        - Per-task metric computation and logging
    
    Attributes:
        model: The underlying UDOP conditional generation model
        lr: Learning rate for optimizer
        weight_decay: Weight decay for regularization
        lr_warmup_steps: Number of warmup steps for learning rate schedule
        max_steps: Maximum number of training steps
        training_step_outputs: Accumulated outputs from training steps
        validation_step_outputs: Accumulated outputs from validation steps
        tasks: Dictionary mapping task names to evaluators
    """
    def __init__(
        self, model_id, lr=5e-5, weight_decay=1e-5, b1=0.9, b2=0.999, 
        lr_warmup_steps=20, max_steps=5000, dropout_rate=0.2,
        print_every_n_steps=100
    ):
        """
        Initialize the UDOP model wrapper.
        
        Args:
            model_id: HuggingFace model identifier (e.g., "microsoft/udop-large")
            lr: Learning rate for Adam optimizer (default: 5e-5)
            weight_decay: Weight decay for regularization (default: 1e-5)
            b1: Beta1 parameter for Adam optimizer (default: 0.9)
            b2: Beta2 parameter for Adam optimizer (default: 0.999)
            lr_warmup_steps: Number of warmup steps for learning rate schedule (default: 20)
            max_steps: Maximum number of training steps for LR schedule (default: 5000)
            dropout_rate: Dropout rate for model regularization (default: 0.2)
            print_every_n_steps: Logging frequency (default: 100)
        
        Note:
            For security, models in the managed list (model_versions.py) are loaded
            with pinned revisions to prevent supply chain attacks. Custom models
            can be used but will not have revision pinning.
        """
        super().__init__()
        self.lr = lr
        self.b1 = b1
        self.b2 = b2
        self.weight_decay = weight_decay
        self.lr_warmup_steps = lr_warmup_steps
        self.max_steps = max_steps
        self.print_every_n_steps = print_every_n_steps
        
        # Load model with pinned revision for security (addresses B615 finding)
        revision = get_model_revision(model_id) if model_id in ["microsoft/udop-large"] else None
        if revision:
            print(f"Loading model {model_id} with pinned revision: {revision}")
            self.model = UdopForConditionalGeneration.from_pretrained(
                model_id, revision=revision, dropout_rate=dropout_rate
            )
        else:
            # nosec B615 - Sample training code for demonstration purposes
            # This fallback path is only for custom models during development/testing
            # Production deployments should use pinned revisions from model_versions.py
            print(f"Loading model {model_id} without revision pinning (not in managed list)")
            self.model = UdopForConditionalGeneration.from_pretrained(
                model_id, dropout_rate=dropout_rate
            )
        
        # Storage for step outputs (used for epoch-end metric computation)
        self.training_step_outputs = []
        self.validation_step_outputs = []
        self.tasks = {}  # Maps task names to evaluators

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        """
        Perform a prediction step (used during inference).
        
        Args:
            batch: Input batch containing model_inputs and evaluator
            batch_idx: Index of the current batch
            dataloader_idx: Index of the dataloader (for multi-dataloader setups)
        
        Returns:
            Decoded model output (predicted text)
        """
        return batch['evaluator'].decode_model_output(
            self.model.forward(**batch['model_inputs'])
        )

    def generic_step(self, batch, batch_idx, subset='train'):
        """
        Generic training/validation step that handles both batched and non-batched modes.
        
        This method supports two data formats:
        1. Original format (batch_size=1): batch contains 'model_inputs' dict
        2. Batched format (batch_size>1): batch contains direct tensor keys
        
        Args:
            batch: Input batch (format depends on batching mode)
            batch_idx: Index of the current batch
            subset: Either 'train' or 'val' for logging purposes
        
        Returns:
            tuple: (step_outputs dict, loss tensor)
                - step_outputs contains model predictions, targets, and task name
                - loss is the computed loss value
        
        Note:
            Handles OOM errors gracefully by printing shapes and returning zero loss.
            Supports both single-sample and batched prediction decoding.
        """
        after_mem = torch.cuda.memory_allocated(device=None)

        # Log memory usage and learning rate
        self.log("memory_usage_gb", after_mem/1e9, prog_bar=False)
        self.log("lr_times_1m", self.scheduler.get_lr()[0] * 1000000, prog_bar=True)

        # Handle both old format (model_inputs dict) and new format (direct keys)
        if 'model_inputs' in batch:
            # Old format - batch_size=1 with custom collate
            model_inputs = batch['model_inputs']
        else:
            # New format - batched with padding
            model_inputs = {
                'input_ids': batch['input_ids'],
                'attention_mask': batch['attention_mask'],
                'bbox': batch['bbox'],
                'pixel_values': batch['pixel_values'],
                'labels': batch['labels']
            }
        
        try:
            model_output = self.model.forward(**model_inputs)
            lss = model_output.loss
            self.log(f"{subset}_loss", lss, sync_dist=True, prog_bar=True)
        except torch.cuda.OutOfMemoryError as e:
            # Handle OOM gracefully - print diagnostics and return zero loss
            print(str(e))
            for k, v in model_inputs.items():
                print(f"{k}, of shape {v.shape}")
            # Return early with zero loss - can't decode without model output
            return {"model_output": [], "targets": [], "task": "unknown"}, torch.tensor(0)

        # Handle evaluator - could be single instance (non-batched) or list (batched)
        evaluator = batch['evaluator'] if not isinstance(batch['evaluator'], list) else batch['evaluator'][0]
        task = batch['task'] if not isinstance(batch['task'], list) else batch['task'][0]
        
        self.tasks.setdefault(task, evaluator)
        
        # Handle text_label - normalize to list format
        text_labels = batch['text_label']
        if not isinstance(text_labels, list):
            text_labels = [text_labels]
        
        # Decode model output - handle batched predictions
        batch_size = model_inputs['input_ids'].shape[0] if len(model_inputs['input_ids'].shape) > 1 else 1
        
        if batch_size > 1:
            # Batched mode - decode each sample individually
            decoded_list = []
            for i in range(batch_size):
                # Create single-sample output dict for decoding
                single_output = {"logits": model_output.logits[i:i+1]}
                decoded_list.append(evaluator.decode_model_output(single_output))
            decoded = decoded_list
        else:
            # Single sample mode
            decoded = [evaluator.decode_model_output(model_output)]
        
        step_outputs = {
            "model_output": decoded,
            "targets": text_labels,
            "task": task
        }
        return step_outputs, lss

    def training_step(self, batch, batch_idx):
        """
        Execute a single training step.
        
        Args:
            batch: Input batch
            batch_idx: Index of the current batch
        
        Returns:
            Loss tensor for backpropagation
        """
        step_outputs, lss = self.generic_step(batch, batch_idx, subset='train')
        self.training_step_outputs.append(step_outputs)
        return lss

    def validation_step(self, batch, batch_idx):
        """
        Execute a single validation step.
        
        Args:
            batch: Input batch
            batch_idx: Index of the current batch
        
        Returns:
            Loss tensor for logging
        """
        step_outputs, lss = self.generic_step(batch, batch_idx, subset='val')
        self.validation_step_outputs.append(step_outputs)
        return lss

    def on_train_epoch_end(self):
        """
        Compute and log metrics at the end of each training epoch.
        
        Aggregates predictions and targets from all training steps, computes
        per-task metrics (precision, recall, F1), and logs them. Handles both
        single-sample and batched outputs.
        """
        # Group predictions and targets by task
        d = {t: {
            'predictions': [],
            'targets': []
        } for t in self.tasks.keys()}
        
        # Flatten predictions and targets (handle both single items and lists)
        for o in self.training_step_outputs:
            if o['task'] in d:
                preds = o['model_output'] if isinstance(o['model_output'], list) else [o['model_output']]
                targs = o['targets'] if isinstance(o['targets'], list) else [o['targets']]
                d[o['task']]['predictions'].extend(preds)
                d[o['task']]['targets'].extend(targs)
        
        # Compute and log metrics for each task
        for k, v in d.items():
            if len(v['predictions']) > 0:
                evaluator = self.tasks[k]
                metrics = evaluator.compute_metrics(v['predictions'], v['targets'])
                for k_, v_ in metrics.items():
                    self.log(f"train_{k_}", v_, sync_dist=True, prog_bar=True)
        
        self.training_step_outputs.clear()

    def on_validation_epoch_end(self):
        """
        Compute and log metrics at the end of each validation epoch.
        
        Aggregates predictions and targets from all validation steps, computes
        per-task metrics (precision, recall, F1), and logs them. Handles both
        single-sample and batched outputs.
        """
        # Group predictions and targets by task
        d = {t: {
            'predictions': [],
            'targets': []
        } for t in self.tasks.keys()}
        
        # Flatten predictions and targets (handle both single items and lists)
        for o in self.validation_step_outputs:
            if o['task'] in d:
                preds = o['model_output'] if isinstance(o['model_output'], list) else [o['model_output']]
                targs = o['targets'] if isinstance(o['targets'], list) else [o['targets']]
                d[o['task']]['predictions'].extend(preds)
                d[o['task']]['targets'].extend(targs)
        
        # Compute and log metrics for each task
        for k, v in d.items():
            if len(v['predictions']) > 0:
                evaluator = self.tasks[k]
                metrics = evaluator.compute_metrics(v['predictions'], v['targets'])
                for k_, v_ in metrics.items():
                    self.log(f"val_{k_}", v_, sync_dist=True, prog_bar=True)
        
        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        """
        Configure optimizer and learning rate scheduler.
        
        Uses Adam optimizer with cosine annealing learning rate schedule with warmup.
        The learning rate is updated at each training step (not per epoch) for
        fine-grained control.
        
        Returns:
            tuple: ([optimizer], [scheduler_config])
                - optimizer: Adam optimizer with configured parameters
                - scheduler_config: Dict with scheduler and update interval
        
        Note:
            The scheduler updates at each step (not epoch) to provide smooth
            learning rate transitions, especially important for the warmup phase.
        """
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
            betas=(self.b1, self.b2)
        )
        
        # Cosine schedule with linear warmup
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, 
            num_warmup_steps=self.lr_warmup_steps,
            num_training_steps=self.max_steps
        )
        
        self.scheduler = scheduler
        
        # Update LR at each step (not epoch) for smooth transitions
        return [optimizer], [{"scheduler": scheduler, "interval": "step"}]
