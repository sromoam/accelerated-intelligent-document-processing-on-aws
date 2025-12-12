# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Baseline inference implementation using default HuggingFace weights.
Falls back to pretrained model if no checkpoint is found.
"""

import json
import logging
import os
import torch

from transformers import AutoProcessor, UdopEncoderDecoderModel

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
    Load model - uses checkpoint if available, otherwise loads pretrained HF weights.
    """
    logger.info("===== Starting baseline model loading... =====")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    model_id = os.getenv("BASE_MODEL", "microsoft/udop-large")
    checkpoint_path = os.path.join(model_dir, "best_model.ckpt")
    
    # Check if checkpoint exists
    if os.path.exists(checkpoint_path):
        logger.info(f"Loading fine-tuned model from checkpoint: {checkpoint_path}")
        from model import UDOPModel
        model = UDOPModel.load_from_checkpoint(
            checkpoint_path=checkpoint_path,
            model_id=model_id
        )
        model = model.model  # Extract the HF model from Lightning wrapper
    else:
        logger.info(f"No checkpoint found, loading pretrained weights from {model_id}")
        revision = get_model_revision(model_id) if model_id in ["microsoft/udop-large"] else None
        
        # Force download with explicit cache dir to avoid timeout issues
        cache_dir = os.getenv("TRANSFORMERS_CACHE", "/tmp/transformers_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        if revision:
            logger.info(f"Using pinned revision: {revision}")
            logger.info(f"Downloading model to {cache_dir}...")
            model = UdopEncoderDecoderModel.from_pretrained(
                model_id, 
                revision=revision,
                cache_dir=cache_dir,
                local_files_only=False
            )
        else:
            logger.info(f"Downloading model to {cache_dir}...")
            model = UdopEncoderDecoderModel.from_pretrained(
                model_id,
                cache_dir=cache_dir,
                local_files_only=False
            )
    
    model.to(device)
    model.eval()
    
    # Load processor with pinned revision
    revision = get_model_revision(model_id) if model_id in ["microsoft/udop-large"] else None
    if revision:
        logger.info(f"Loading processor for {model_id} with pinned revision: {revision}")
        processor = AutoProcessor.from_pretrained(model_id, revision=revision, apply_ocr=False)
    else:
        logger.info(f"Loading processor for {model_id} without revision pinning")
        processor = AutoProcessor.from_pretrained(model_id, apply_ocr=False)
    
    # Load or create default validation prompt
    prompt_path = os.path.join(model_dir, "validation_prompt.json")
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r') as f:
            validation_prompt = json.load(f)['validation_prompt']
    else:
        validation_prompt = "What is the document type?"
        logger.info(f"Using default validation prompt: {validation_prompt}")
    
    logger.info("===== Model successfully loaded =====")
    return {
        "model": model,
        "processor": processor,
        "device": device,
        "validation_prompt": validation_prompt
    }


def predict_fn(input_data, model):
    """
    Standard prediction with default generation parameters.
    """
    logger.info("===== Starting prediction... =====")
    device = model["device"]
    model_instance = model["model"]
    
    try:
        ih = InferenceHelper()
        prompt = input_data.get("prompt") or model['validation_prompt']
        
        prepped_model_input = ih.prepare_model_input(
            processor=model["processor"],
            image=input_data["image"],
            textract=input_data["textract"],
            prompt=prompt
        )
        
        for key in prepped_model_input:
            if isinstance(prepped_model_input[key], torch.Tensor):
                prepped_model_input[key] = prepped_model_input[key].to(device)
        
        # Standard generation with default parameters
        model_output = model_instance.generate(**prepped_model_input)
        text_output = model["processor"].batch_decode(model_output, skip_special_tokens=True)[0]
        
        logger.info(f"Prediction: {text_output}")
        
        return {"prediction": text_output, "prompt": prompt} if input_data.get('debug') \
            else {"prediction": text_output}
            
    except Exception as e:
        logger.error("===== Error during prediction: %s =====", str(e), exc_info=True)
        raise


def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    logger.info("Processing input with content type: %s", request_content_type)
    try:
        if request_content_type == "application/json":
            request = json.loads(request_body)
            ih = InferenceHelper()
            request['image'] = ih._get_image_from_s3(request['input_image'])
            request['textract'] = ih._get_json_from_s3(request['input_textract'])
            logger.info("===== Successfully parsed JSON input =====")
        else:
            request = request_body
            logger.info("Using raw input")
        return request
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", str(e))
        raise ValueError(f"Invalid JSON input: {str(e)}")
    except Exception as e:
        logger.error("Error in input processing: %s", str(e), exc_info=True)
        raise


def output_fn(prediction, response_content_type):
    """
    Serialize and prepare the prediction output
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
