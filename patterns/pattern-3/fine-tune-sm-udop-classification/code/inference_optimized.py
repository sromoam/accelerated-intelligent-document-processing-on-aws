# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Optimized inference implementation for UDOP document classification.

This module provides high-performance inference with:
- torch.compile() for faster execution
- Optimized generation parameters for classification
- torch.no_grad() for memory efficiency
- Backend optimizations (TF32, cuDNN benchmark)
- Model warmup for consistent latency
"""

import json
import logging
import os
import torch

import numpy as np

from PIL import Image
from transformers import AutoProcessor

from model import UDOPModel
from utils import InferenceHelper

# Import for secure model version management
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_versions import get_model_revision


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def model_fn(model_dir):
    """
    Load and optimize the model for inference.
    
    Applies several optimizations:
    1. Loads model in eval mode
    2. Moves to GPU with optimal dtype
    3. Enables backend optimizations (TF32, cuDNN benchmark)
    4. Optionally compiles with torch.compile()
    5. Warms up the model with dummy inputs
    
    Args:
        model_dir: Directory containing the trained model checkpoint
    
    Returns:
        dict: Model artifacts including compiled model, processor, device, and prompt
    """
    logger.info("===== Starting optimized model loading... =====")
    
    # Determine device and enable backend optimizations
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    if device == "cuda":
        # Enable TF32 for faster matmul on Ampere+ GPUs
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        # Enable cuDNN benchmark for optimal kernel selection
        torch.backends.cudnn.benchmark = True
        logger.info("Enabled TF32 and cuDNN benchmark mode")
    
    # Load model
    model_id = os.getenv("BASE_MODEL", "microsoft/udop-large")
    logger.info(f"Loading model from checkpoint: {model_dir}")
    
    model = UDOPModel.load_from_checkpoint(
        checkpoint_path=os.path.join(model_dir, "best_model.ckpt"),
        model_id=model_id
    )
    
    # Move to device and set to eval mode
    model.to(device)
    model.eval()
    
    # Disable gradient computation for inference
    for param in model.parameters():
        param.requires_grad = False
    
    logger.info("Model loaded and set to eval mode")
    
    # Load processor with pinned revision
    revision = get_model_revision(model_id) if model_id in ["microsoft/udop-large"] else None
    if revision:
        logger.info(f"Loading processor for {model_id} with pinned revision: {revision}")
        processor = AutoProcessor.from_pretrained(model_id, revision=revision, apply_ocr=False)
    else:
        logger.info(f"Loading processor for {model_id} without revision pinning")
        processor = AutoProcessor.from_pretrained(model_id, apply_ocr=False)
    
    # Load validation prompt
    with open(os.path.join(model_dir, "validation_prompt.json"), 'r') as f:
        validation_prompt = json.load(f)['validation_prompt']
    
    # Optional: Compile model with torch.compile for faster inference
    # Uncomment to enable (requires PyTorch 2.0+)
    compile_model = os.getenv("COMPILE_MODEL", "false").lower() == "true"
    if compile_model and device == "cuda":
        logger.info("Compiling model with torch.compile...")
        try:
            model.model = torch.compile(
                model.model,
                mode="reduce-overhead",  # Optimize for inference
                backend="inductor"
            )
            logger.info("Model compiled successfully")
        except Exception as e:
            logger.warning(f"Model compilation failed, using eager mode: {e}")
    
    # Warmup: Run a few dummy inferences to compile/optimize kernels
    if device == "cuda":
        logger.info("Warming up model with dummy inputs...")
        try:
            dummy_image = torch.randn(1, 3, 224, 224, device=device)
            dummy_input_ids = torch.randint(0, 1000, (1, 128), device=device)
            dummy_bbox = torch.zeros(1, 128, 4, device=device)
            dummy_attention_mask = torch.ones(1, 128, device=device)
            
            with torch.no_grad():
                for _ in range(3):  # Warmup iterations
                    _ = model.model.generate(
                        input_ids=dummy_input_ids,
                        bbox=dummy_bbox,
                        pixel_values=dummy_image,
                        attention_mask=dummy_attention_mask,
                        max_new_tokens=4,
                        num_beams=1,
                        do_sample=False
                    )
            logger.info("Model warmup complete")
        except Exception as e:
            logger.warning(f"Warmup failed (non-critical): {e}")
    
    logger.info("===== Model successfully loaded and optimized =====")
    
    return {
        "model": model,
        "processor": processor,
        "device": device,
        "validation_prompt": validation_prompt
    }


def predict_fn(input_data, model):
    """
    Optimized prediction function for document classification.
    
    Optimizations applied:
    1. torch.no_grad() for memory efficiency
    2. Minimal generation parameters (max_new_tokens=4, num_beams=1)
    3. Early stopping enabled
    4. No sampling (deterministic)
    
    Args:
        input_data: Dict containing image, textract, prompt, and debug flag
        model: Model artifacts from model_fn()
    
    Returns:
        dict: Prediction result with optional debug info
    """
    logger.info("===== Starting optimized prediction... =====")
    
    device = model["device"]
    model_instance = model["model"]
    
    try:
        ih = InferenceHelper()
        prompt = input_data.get("prompt") or model['validation_prompt']
        
        # Prepare model inputs
        prepped_model_input = ih.prepare_model_input(
            processor=model["processor"],
            image=input_data["image"],
            textract=input_data["textract"],
            prompt=prompt
        )
        
        # Move tensors to device
        for key in prepped_model_input:
            if isinstance(prepped_model_input[key], torch.Tensor):
                prepped_model_input[key] = prepped_model_input[key].to(device)
        
        # Optimized generation for classification
        # Use torch.no_grad() for better compatibility with torch.compile
        with torch.no_grad():
            model_output = model_instance.model.generate(
                **prepped_model_input,
                max_new_tokens=4,        # Classification labels are short
                num_beams=1,             # No beam search (greedy decoding)
                do_sample=False,         # Deterministic output
                early_stopping=True,     # Stop at EOS token
                use_cache=True,          # Enable KV cache
                return_dict_in_generate=False  # Simpler output format
            )
        
        # Decode prediction
        text_output = model["processor"].batch_decode(
            model_output, 
            skip_special_tokens=True
        )[0]
        
        logger.info(f"Prediction: {text_output}")
        
        # Return with optional debug info
        if input_data.get('debug', False):
            return {
                "prediction": text_output,
                "prompt": prompt,
                "input_shape": {
                    k: v.shape if isinstance(v, torch.Tensor) else None
                    for k, v in prepped_model_input.items()
                }
            }
        else:
            return {"prediction": text_output}
            
    except Exception as e:
        logger.error("===== Error during prediction: %s =====", str(e), exc_info=True)
        raise


def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input.
    
    Args:
        request_body: Raw request body
        request_content_type: Content type of the request
    
    Returns:
        dict: Parsed input data ready for prediction
    """
    logger.info("Processing input with content type: %s", request_content_type)
    
    try:
        if request_content_type == "application/json":
            request = json.loads(request_body)
            ih = InferenceHelper()
            
            # Load image and textract from S3
            request['image'] = ih._get_image_from_s3(request['input_image'])
            request['textract'] = ih._get_json_from_s3(request['input_textract'])
            
            logger.info("===== Successfully parsed JSON input =====")
        else:
            request = request_body
            logger.info("Using raw input")
        
        return request
        
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", str(e))
        logger.error("Received body: %s", request_body)
        raise ValueError(f"Invalid JSON input: {str(e)}")
    except Exception as e:
        logger.error("Error in input processing: %s", str(e), exc_info=True)
        raise


def output_fn(prediction, response_content_type):
    """
    Serialize and prepare the prediction output.
    
    Args:
        prediction: Prediction result from predict_fn
        response_content_type: Desired response content type
    
    Returns:
        str: Serialized response
    """
    logger.info("Formatting output with content type: %s", response_content_type)
    
    try:
        if response_content_type == "application/json":
            response = json.dumps(prediction)
            logger.info("===== Formatted JSON response =====")
        else:
            response = str(prediction)
            logger.info("===== Formatted string response =====")
        
        return response
        
    except Exception as e:
        logger.error("Error in output formatting: %s", str(e), exc_info=True)
        raise
