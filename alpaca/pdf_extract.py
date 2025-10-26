import sys
import os
import base64
import io
from PIL import Image
from pdf2image import convert_from_path
from groq import Groq
from dotenv import load_dotenv
from vector_db import VectorDBManager
from logging_config import setup_logger, ProgressLogger

# Set up logger
logger = setup_logger(__name__, "pdf_extraction.log")

def image_to_base64(image, format="JPEG"):
    """Converts a PIL Image to a base64 encoded string."""
    # Resize image: max side 1024px
    max_size = 1024
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        logger.debug(f"Resized image to {new_size}")
    
    # Convert to grayscale
    image = image.convert('L')
    
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_text_with_groq(pdf_path, progress_callback=None):
    """
    Extracts text from a PDF (even scanned) using Groq and Llama 3.2 Vision.
    
    Args:
        pdf_path (str): The file path to the PDF.
        progress_callback (callable): Optional callback function for progress updates.
                                     Called with (current_page, total_pages, status_message)
        
    Returns:
        str: The extracted text from all pages.
    """
    logger.info(f"Starting PDF extraction for: {pdf_path}")
    
    # Load environment variables (for GROQ_API_KEY)
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        error_msg = "GROQ_API_KEY not found in environment variables"
        logger.error(error_msg)
        return {"error": error_msg}
                
    client = Groq(api_key=api_key)
    model_name = "meta-llama/llama-4-scout-17b-16e-instruct" # Groq model ID for Llama 3.2 11B Vision
    logger.info(f"Using Groq model: {model_name}")

    if not os.path.exists(pdf_path):
        error_msg = f"File not found at {pdf_path}"
        logger.error(error_msg)
        return {"error": error_msg}

    all_text = ""

    # 1. Convert PDF to a list of PIL Images
    logger.info(f"Converting PDF to images: {pdf_path}")
    try:
        images = convert_from_path(pdf_path)
        num_pages = len(images)
        logger.info(f"Successfully converted PDF to {num_pages} pages")
        
        if progress_callback:
            progress_callback(0, num_pages, "PDF converted to images")
    except Exception as e:
        error_msg = f"Failed to convert PDF to images. Check if poppler is installed. Error: {e}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}

    # 2. Process each image with Groq
    progress = ProgressLogger(logger, num_pages, "PDF page extraction")
    
    for i, image in enumerate(images):
        page_num = i + 1
        logger.info(f"Processing page {page_num}/{num_pages} with Groq Vision API")
        
        if progress_callback:
            progress_callback(page_num, num_pages, f"Extracting text from page {page_num}")
        
        # Convert image to base64 data URL
        try:
            b64_image = image_to_base64(image)
            data_url = f"data:image/jpeg;base64,{b64_image}"
            logger.debug(f"Page {page_num}: Image converted to base64 ({len(b64_image)} chars)")
        except Exception as e:
            error_msg = f"Failed to convert page {page_num} to base64: {e}"
            logger.error(error_msg, exc_info=True)
            all_text += f"--- Page {page_num} (ERROR) ---\nFailed to process image\n\n"
            continue
        
        try:
            # Send to Groq API
            logger.debug(f"Page {page_num}: Sending request to Groq API")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this document page. "
                                        "Respond with only the raw text content, nothing else. "
                                        "Do not add any commentary or formatting."
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
                max_tokens=4096 # Set a high limit for text-heavy pages
            )
            
            page_text = response.choices[0].message.content
            logger.info(f"Page {page_num}: Successfully extracted {len(page_text)} characters")
            
            all_text += f"--- Page {page_num} ---\n"
            all_text += page_text.strip() + "\n\n"
            
            progress.update(message=f"Page {page_num} complete ({len(page_text)} chars)")
            
        except Exception as e:
            error_msg = f"Error extracting text from page {page_num}: {e}"
            logger.error(error_msg, exc_info=True)
            all_text += f"--- Page {page_num} (ERROR) ---\nFailed to extract text: {str(e)}\n\n"
            
            if progress_callback:
                progress_callback(page_num, num_pages, f"Error on page {page_num}")

    progress.complete(f"Extracted text from {num_pages} pages")
    logger.info(f"Extraction complete. Total text length: {len(all_text)} characters")
    
    if progress_callback:
        progress_callback(num_pages, num_pages, "Extraction complete")
    
    return all_text

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("PDF Extraction Script Started")
    logger.info("="*60)
    
    # Initialize vector database manager
    db_manager = VectorDBManager()
    
    pdf_path = "pdfs/RISCV_CALL.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    logger.info(f"Processing PDF: {pdf_path}")
    extracted_text = extract_text_with_groq(pdf_path)
    
    # Check for errors
    if isinstance(extracted_text, dict) and "error" in extracted_text:
        logger.error(f"Extraction failed: {extracted_text['error']}")
        print(f"\n❌ Extraction failed: {extracted_text['error']}")
        sys.exit(1)
    
    if extracted_text:
        logger.info(f"Extraction successful. Total text length: {len(extracted_text)} characters")
        print("\n--- EXTRACTED TEXT (Groq & Llama 3.2 Vision) ---")
        print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
        
        # Store extracted text in pdf_texts folder
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join("pdf_texts", f"{base_name}.txt")
        
        # Ensure pdf_texts directory exists
        os.makedirs("pdf_texts", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        logger.info(f"Saved extracted text to {output_path}")
        print(f"\n✅ Saved extracted text to {output_path}")
        
        # Add to vector database
        logger.info("Adding extracted text to vector database")
        print("\n--- Adding to Vector Database ---")
        collection_name = "mind_palace_pdfs"  # Can be customized per floor
        try:
            num_chunks = db_manager.add_pdf_to_vector_db(
                collection_name=collection_name,
                pdf_text=extracted_text,
                pdf_filename=base_name,
                metadata={"source_path": pdf_path}
            )
            logger.info(f"Successfully stored {num_chunks} chunks in vector database")
            print(f"\n✅ Successfully stored {num_chunks} chunks in vector database!")
            
            # Show collection stats
            stats = db_manager.get_collection_stats(collection_name)
            logger.info(f"Collection '{collection_name}' now contains {stats['count']} total chunks")
            print(f"Collection '{collection_name}' now contains {stats['count']} total chunks")
        except Exception as e:
            logger.error(f"Error adding to vector database: {e}", exc_info=True)
            print(f"❌ Error adding to vector database: {e}")
    else:
        logger.error("Extraction returned empty result")
        print("❌ Extraction failed - no text returned")
    
    logger.info("="*60)
    logger.info("PDF Extraction Script Completed")
    logger.info("="*60)
