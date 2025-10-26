"""
Fal.AI Service for object detection and image extraction
"""
import os
import base64
import requests
import time
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

FAL_API_KEY = "cdb3a529-42cd-4190-8930-9ff21c2ef1a9:ffd4e9df946a00d3977f2d6c903a0551"

# Using Qwen Image Edit for image-to-image transformation
# This model takes a room photo and extracts specific objects from it
FAL_SUBMIT_URL = "https://queue.fal.run/fal-ai/qwen-image-edit/image-to-image"
FAL_STATUS_URL = "https://queue.fal.run/fal-ai/qwen-image-edit/image-to-image/requests"


def extract_object_from_room(
    room_image_url: str,
    object_name: str,
    object_description: str
) -> Dict:
    """
    Extract a specific object from a room image using fal.ai qwen-image-edit
    
    Args:
        room_image_url: URL or base64 data URI of the room image
        object_name: Name of the object to extract
        object_description: Description of the object
        
    Returns:
        Dict with 'image_url' containing the extracted object image
    """
    logger.info(f"Extracting object '{object_name}' from room image")
    
    # Create prompt to extract and isolate the object
    # The prompt should instruct the model to:
    # 1. Focus on the specific object
    # 2. Crop tightly around it
    # 3. Remove background/context
    # 4. Make it suitable for memory palace visualization
    prompt = (
        f"Show only the {object_name}. "
        f"Isolate and crop tightly around the {object_name}. "
        f"Remove all background and other objects. "
        f"Clean white background. Centered composition. "
        f"Product photography style."
    )
    
    payload = {
        "prompt": prompt,
        "image_url": room_image_url,
        "num_inference_steps": 28,  # Good balance of quality and speed
        "guidance_scale": 5.0,  # Higher for better prompt adherence
        "strength": 0.9,  # High strength to make significant changes
        "num_images": 1,
        "enable_safety_checker": False,
        "output_format": "jpeg"
    }
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Step 1: Submit request to fal.ai queue
        logger.info(f"Submitting job to fal.ai queue")
        logger.debug(f"Payload: {payload}")
        
        response = requests.post(
            FAL_SUBMIT_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Submit response status: {response.status_code}")
        logger.debug(f"Submit response: {response.text}")
        
        if response.status_code not in [200, 201]:
            logger.error(f"Fal.AI submit failed: {response.status_code} - {response.text}")
            raise Exception(f"Fal.AI submit failed: {response.text}")
        
        submit_result = response.json()
        request_id = submit_result.get("request_id")
        
        if not request_id:
            logger.error(f"No request_id in response: {submit_result}")
            raise Exception("No request_id returned from fal.ai")
        
        logger.info(f"Job submitted with request_id: {request_id}")
        
        # Step 2: Poll for result
        status_url = f"{FAL_STATUS_URL}/{request_id}"
        max_attempts = 60  # 60 attempts * 2 seconds = 2 minutes max
        
        for attempt in range(max_attempts):
            time.sleep(2)  # Wait 2 seconds between polls
            
            status_response = requests.get(
                status_url,
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code != 200:
                logger.warning(f"Status check failed: {status_response.status_code}")
                continue
            
            status_result = status_response.json()
            status = status_result.get("status")
            
            logger.info(f"Attempt {attempt + 1}: Status = {status}")
            
            if status == "COMPLETED":
                # Get the result
                result_data = status_result.get("response", {})
                logger.info(f"Completed result data: {result_data}")
                
                if 'images' in result_data and len(result_data['images']) > 0:
                    image_url = result_data['images'][0]['url']
                    logger.info(f"Successfully extracted object image: {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "object_name": object_name
                    }
                else:
                    logger.error(f"No images in completed result: {result_data}")
                    return {
                        "success": False,
                        "error": "No images in fal.ai result",
                        "details": result_data
                    }
            
            elif status == "FAILED":
                error = status_result.get("error", "Unknown error")
                logger.error(f"Job failed: {error}")
                raise Exception(f"Fal.ai job failed: {error}")
        
        # Timeout
        raise Exception("Timeout waiting for fal.ai result")
            
    except Exception as e:
        logger.error(f"Error extracting object: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


# NOTE: generate_object_image function removed - we only use image-to-image extraction
# If you need to fallback to text-to-image generation, the function can be restored
# from version control or re-implemented using fal-ai/flux/schnell model
