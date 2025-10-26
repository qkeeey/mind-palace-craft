import sys
import os
import base64
import io
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
import json


def image_to_base64(image_path):
    """Converts an image file to a base64 encoded string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            # Convert to RGB if not already (some formats like Png might be RGBA)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")  # Use JPEG for smaller size and common compatibility
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Could not process image at {image_path}: {e}")


def get_image_info_with_groq(image_path):
    """
    Analyzes an image using Groq's Llama 3.2 Vision model
    and returns object name and description in JSON format.

    Args:
        image_path (str): The file path to the image.

    Returns:
        dict: A dictionary containing 'object_name' and 'object_description',
              or an error message if something goes wrong.
    """
    # Load environment variables (for GROQ_API_KEY)
    load_dotenv()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"error": ("GROQ_API_KEY not found. "
                          "Please create a .env file and add your key. "
                          "See .env.example for details.")}

    client = Groq(api_key=api_key)
    model_name = "meta-llama/llama-4-scout-17b-16e-instruct"  # Groq model ID for Llama 3.2 11B Vision

    try:
        # 1. Convert image to base64 data URL
        b64_image = image_to_base64(image_path)
        data_url = f"data:image/jpeg;base64,{b64_image}"

        print(f"Analyzing image: {image_path} with Groq ({model_name})...")

        # 2. Define the prompt for JSON output
        # prompt_text = (
        #     """
        #     You are a careful vision labeler for a memory-palace app.
        #     Given a single object photo, return:
        #     - object_name: 2–6 words, clear and practical.
        #     - short_description: 25–40 words describing visible materials, color/shape, notable features, and typical usage.
        #
        #     Rules:
        #     - Describe only what is clearly visible.
        #     - If multiple objects are visible, focus on the most prominent, centered, or largest one.
        #     - You can include short context information about its environment (5-10 words).
        #     - Describe the characteristics or structure in detail
        #     - Keep language neutral and non-figurative; avoid emojis.
        #     - Output strictly valid JSON with keys: object_name, short_description. No extra text.
        #     Format of output json:
        #     {
        #       "object_name": "string, 2–6 words",
        #       "short_description": "string, 25–40 words"
        #     }
        #     """
        # )
        prompt_text = (
            """
            Identify all the objects on the photo and send it to me as a list.
            """
        )

        # 3. Send to Groq API
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,  # Adjust creativity
            max_tokens=500  # Sufficient for description
        )

        raw_content = response.choices[0].message.content
        print(f"Raw API response content: {raw_content}")  # For debugging

        # 4. Parse the JSON response
        try:
            json_output = json.loads(raw_content)
            # Basic validation of the JSON structure
            if "object_name" in json_output and "object_description" in json_output:
                return json_output
            else:
                return {"error": f"API returned invalid JSON structure: {raw_content}"}
        except json.JSONDecodeError:
            return {"error": f"API did not return valid JSON: {raw_content}"}

    except FileNotFoundError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


if __name__ == "__main__":

    image_file_path = "pdfs/5467668469785953711.jpg"

    result = get_image_info_with_groq(image_file_path)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\n--- Image Analysis Result ---")
        print(json.dumps(result, indent=2))
