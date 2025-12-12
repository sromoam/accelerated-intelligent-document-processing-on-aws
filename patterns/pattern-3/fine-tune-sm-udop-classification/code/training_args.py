"""
Shared argument parser configuration for UDOP training.

This module provides reusable argument parsers that can be inherited by both
local training scripts and SageMaker training scripts using argparse parents.
"""

import argparse
import os
import torch


def get_model_args_parser():
    """
    Get argument parser for model-related hyperparameters.
    
    Returns:
        ArgumentParser configured with model arguments (add_help=False for parent usage)
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    model_group = parser.add_argument_group(
        'Model Configuration',
        'Arguments for model architecture and initialization'
    )
    
    model_group.add_argument(
        "--base_model",
        type=str,
        default="microsoft/udop-large",
        help="HuggingFace model identifier (e.g., microsoft/udop-large)"
    )
    
    model_group.add_argument(
        "--dropout_rate",
        type=float,
        default=0.2,
        help="Dropout rate for model regularization (default: 0.2)"
    )
    
    return parser


def get_optimizer_args_parser():
    """
    Get argument parser for optimizer-related hyperparameters.
    
    Returns:
        ArgumentParser configured with optimizer arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    optimizer_group = parser.add_argument_group(
        'Optimizer Configuration',
        'Arguments for optimizer and learning rate schedule'
    )
    
    optimizer_group.add_argument(
        "--lr",
        type=float,
        default=5e-4,
        help="Learning rate for Adam optimizer (default: 5e-4)"
    )
    
    optimizer_group.add_argument(
        "--b1",
        type=float,
        default=0.9,
        help="Beta1 parameter for Adam optimizer (default: 0.9)"
    )
    
    optimizer_group.add_argument(
        "--b2",
        type=float,
        default=0.999,
        help="Beta2 parameter for Adam optimizer (default: 0.999)"
    )
    
    optimizer_group.add_argument(
        "--weight_decay",
        type=float,
        default=1e-4,
        help="Weight decay for L2 regularization (default: 1e-4)"
    )
    
    optimizer_group.add_argument(
        "--lr_warmup_steps",
        type=int,
        default=60,
        help="Number of warmup steps for learning rate schedule (default: 60)"
    )
    
    return parser


def get_training_args_parser():
    """
    Get argument parser for training loop configuration.
    
    Returns:
        ArgumentParser configured with training arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    training_group = parser.add_argument_group(
        'Training Configuration',
        'Arguments for training loop, epochs, and steps'
    )
    
    training_group.add_argument(
        "--max_epochs",
        type=int,
        default=3,
        help="Maximum number of training epochs (default: 3)"
    )
    
    training_group.add_argument(
        "--max_steps",
        type=int,
        default=None,
        help="Maximum number of training steps (overrides max_epochs if set)"
    )
    
    training_group.add_argument(
        "--accumulate_grad_batches",
        type=int,
        default=10,
        help="Number of batches to accumulate gradients over (default: 10)"
    )
    
    training_group.add_argument(
        "--patience",
        type=int,
        default=30,
        help="Early stopping patience in epochs (default: 30)"
    )
    
    training_group.add_argument(
        "--fast_dev_run",
        type=int,
        default=None,
        help="Run only N batches for quick testing (default: None, run full training)"
    )
    
    training_group.add_argument(
        "--num_sanity_val_steps",
        type=int,
        default=0,
        help="Number of validation sanity check steps before training (default: 0 for faster startup)"
    )
    
    return parser


def get_data_args_parser():
    """
    Get argument parser for data loading configuration.
    
    Returns:
        ArgumentParser configured with data arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    data_group = parser.add_argument_group(
        'Data Configuration',
        'Arguments for data loading and batching'
    )
    
    data_group.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for training (requires --enable_batching for batch_size > 1)"
    )
    
    data_group.add_argument(
        "--enable_batching",
        type=lambda x: x.lower() == 'true',
        default=False,
        help="Enable batching support with padding (pass 'true' or 'false')"
    )
    
    data_group.add_argument(
        "--num_workers",
        type=int,
        default=4,
        help="Number of data loading workers (default: 4, use 0 for debugging)"
    )
    
    data_group.add_argument(
        "--max_train_samples",
        type=int,
        default=None,
        help="Truncate training dataset to N samples (for faster testing, default: None = use all)"
    )
    
    data_group.add_argument(
        "--max_val_samples",
        type=int,
        default=None,
        help="Truncate validation dataset to N samples (for faster testing, default: None = use all)"
    )
    
    return parser


def get_system_args_parser():
    """
    Get argument parser for system/hardware configuration.
    
    Returns:
        ArgumentParser configured with system arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    system_group = parser.add_argument_group(
        'System Configuration',
        'Arguments for hardware, precision, and distributed training'
    )
    
    system_group.add_argument(
        "--devices",
        type=int,
        default=torch.cuda.device_count(),
        help=f"Number of GPUs to use (default: {torch.cuda.device_count()}, auto-detected)"
    )
    
    system_group.add_argument(
        "--precision",
        type=str,
        default="bf16-true",
        choices=["32", "16", "bf16-true", "bf16-mixed"],
        help="Training precision (default: bf16-true for mixed precision)"
    )
    
    system_group.add_argument(
        "--distributed_strategy",
        type=str,
        default="ddp_find_unused_parameters_true",
        help="PyTorch Lightning distributed strategy (default: ddp_find_unused_parameters_true)"
    )
    
    return parser


def get_logging_args_parser():
    """
    Get argument parser for logging configuration.
    
    Returns:
        ArgumentParser configured with logging arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    logging_group = parser.add_argument_group(
        'Logging Configuration',
        'Arguments for logging and monitoring'
    )
    
    logging_group.add_argument(
        "--print_every_n_steps",
        type=int,
        default=100,
        help="Log metrics every N training steps (default: 100)"
    )
    
    logging_group.add_argument(
        "--verbose",
        type=lambda x: x.lower() == 'true',
        default=True,
        help="Enable verbose logging and progress bars (default: true)"
    )
    
    logging_group.add_argument(
        "--debug_mode",
        type=lambda x: x.lower() == 'true',
        default=False,
        help="Enable debug logging (predictions, labels, shapes) (default: false)"
    )
    
    return parser


def get_path_args_parser():
    """
    Get argument parser for file paths (SageMaker-specific).
    
    Returns:
        ArgumentParser configured with path arguments
    """
    parser = argparse.ArgumentParser(add_help=False)
    
    path_group = parser.add_argument_group(
        'Path Configuration',
        'Arguments for input/output directories (auto-configured on SageMaker)'
    )
    
    path_group.add_argument(
        "--data_dir",
        type=str,
        default=os.environ.get("SM_INPUT_DIR", "/opt/ml/input") + "/data",
        help="Directory containing training and validation data"
    )
    
    path_group.add_argument(
        "--model_dir",
        type=str,
        default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"),
        help="Directory to save the trained model"
    )
    
    path_group.add_argument(
        "--script_dir",
        type=str,
        default=os.environ.get("SM_SCRIPT_DIR", "/opt/ml/code"),
        help="Directory containing training scripts"
    )
    
    path_group.add_argument(
        "--output_dir",
        type=str,
        default=os.environ.get("SM_OUTPUT_DIR", "/opt/ml/output"),
        help="Directory for training outputs and logs"
    )
    
    return parser


def get_all_training_args_parser():
    """
    Get complete argument parser with all training arguments.
    
    Combines all argument groups into a single parser for use in train.py.
    
    Returns:
        ArgumentParser with all training arguments organized into groups
    """
    parser = argparse.ArgumentParser(
        description='Train UDOP model for document classification',
        parents=[
            get_path_args_parser(),
            get_model_args_parser(),
            get_optimizer_args_parser(),
            get_training_args_parser(),
            get_data_args_parser(),
            get_system_args_parser(),
            get_logging_args_parser(),
        ],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    return parser


def get_hyperparameter_args_parser():
    """
    Get argument parser for hyperparameters only (no paths).
    
    Used by SageMaker training script to define which hyperparameters
    can be passed to the training job.
    
    Returns:
        ArgumentParser with hyperparameter arguments (excludes path arguments)
    """
    parser = argparse.ArgumentParser(
        description='UDOP training hyperparameters for SageMaker',
        parents=[
            get_model_args_parser(),
            get_optimizer_args_parser(),
            get_training_args_parser(),
            get_data_args_parser(),
            get_system_args_parser(),
            get_logging_args_parser(),
        ],
        add_help=False,  # Don't add help for parent parser
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    return parser
