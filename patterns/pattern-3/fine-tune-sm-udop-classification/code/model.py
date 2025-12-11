# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

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
    def __init__(
        self, model_id, lr=5e-5, weight_decay=1e-5, b1=0.9, b2=0.999, 
        lr_warmup_steps=20, max_steps=5000, dropout_rate=0.2,
        print_every_n_steps=100
    ):
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
        self.training_step_outputs = []
        self.validation_step_outputs = []
        self.tasks = {}

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        return batch['evaluator'].decode_model_output(
            self.model.forward(**batch['model_inputs'])
        )

    def generic_step(self, batch, batch_idx, subset='train'):
        after_mem = torch.cuda.memory_allocated(device=None)

        # Log memory usage and lr
        self.log("memory_usage_gb", after_mem/1e9, prog_bar=False)
        self.log("lr_times_1m", self.scheduler.get_lr()[0] * 1000000, prog_bar=True)

        try:
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
            
            model_output = self.model.forward(**model_inputs)
            lss = model_output.loss
            self.log(f"{subset}_loss", lss, sync_dist=True, prog_bar=True)
        except torch.cuda.OutOfMemoryError as e:
            print(str(e))
            for k, v in model_inputs.items():
                print(f"{k}, of shape {v.shape}")
            lss = torch.tensor(0)

        # Handle evaluator - could be single instance or batch
        evaluator = batch['evaluator'] if not isinstance(batch['evaluator'], list) else batch['evaluator'][0]
        task = batch['task'] if not isinstance(batch['task'], list) else batch['task'][0]
        
        self.tasks.setdefault(task, evaluator)
        
        # Handle text_label - could be string or list of strings
        text_labels = batch['text_label']
        if not isinstance(text_labels, list):
            text_labels = [text_labels]
        
        # Decode model output - handle batched predictions
        batch_size = model_inputs['input_ids'].shape[0] if len(model_inputs['input_ids'].shape) > 1 else 1
        
        if batch_size > 1:
            # Batched mode - decode each sample
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
        step_outputs, lss = self.generic_step(batch, batch_idx, subset='train')
        self.training_step_outputs.append(step_outputs)
        return lss

    def validation_step(self, batch, batch_idx):
        step_outputs, lss = self.generic_step(batch, batch_idx, subset='val')
        self.validation_step_outputs.append(step_outputs)
        return lss

    def on_train_epoch_end(self):
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
        
        for k, v in d.items():
            if len(v['predictions']) > 0:
                evaluator = self.tasks[k]
                metrics = evaluator.compute_metrics(v['predictions'], v['targets'])
                for k_, v_ in metrics.items():
                    self.log(f"train_{k_}", v_, sync_dist=True, prog_bar=True)
        self.training_step_outputs.clear()

    def on_validation_epoch_end(self):
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
        
        for k, v in d.items():
            if len(v['predictions']) > 0:
                evaluator = self.tasks[k]
                metrics = evaluator.compute_metrics(v['predictions'], v['targets'])
                for k_, v_ in metrics.items():
                    self.log(f"val_{k_}", v_, sync_dist=True, prog_bar=True)
        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
            betas=(self.b1, self.b2)
        )
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=self.lr_warmup_steps,
            num_training_steps=self.max_steps
        )
        self.scheduler = scheduler
        return [optimizer], [{"scheduler": scheduler, "interval": "step"}] # Update LR in each step, not epoch
