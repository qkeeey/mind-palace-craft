"""
FastAPI server for Vector Database RAG queries
Exposes HTTP endpoints for the vector database and RAG service
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import tempfile
import os

from vector_db import VectorDBManager
from rag_service import RAGService
from concept_generator import ConceptGenerator
from association_generator import AssociationGenerator
from pdf_extract import extract_text_with_groq
from logging_config import setup_logger

# Set up logger
logger = setup_logger(__name__, "api_server.log")

# Initialize FastAPI app
app = FastAPI(
    title="MindPalace Vector DB API",
    description="REST API for vector database and RAG queries",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger.info("Initializing services...")
db_manager = VectorDBManager()
rag_service = RAGService()
concept_generator = ConceptGenerator()
association_generator = AssociationGenerator()
logger.info("Services initialized successfully")

# Request/Response models
class QueryRequest(BaseModel):
    collection_name: str
    question: str
    n_results: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]

class AddPDFRequest(BaseModel):
    collection_name: str
    pdf_text: str
    pdf_filename: str
    metadata: Optional[Dict] = None

class AddPDFResponse(BaseModel):
    success: bool
    chunks_added: int
    message: str

class GenerateConceptsRequest(BaseModel):
    pdf_text: str
    num_concepts: Optional[int] = 10

class GenerateConceptsResponse(BaseModel):
    concepts: List[Dict[str, str]]

class GenerateAssociationsRequest(BaseModel):
    concepts: List[Dict[str, str]]
    room_objects: List[Dict[str, str]]
    pdf_text: Optional[str] = None

class GenerateAssociationsResponse(BaseModel):
    associations: List[Dict]

class ExtractPDFRequest(BaseModel):
    pdf_path: str

class ExtractPDFResponse(BaseModel):
    extracted_text: str
    page_count: int
    message: str

class CollectionStatsResponse(BaseModel):
    name: str
    count: int
    exists: bool

class ExplainRequest(BaseModel):
    floor_id: str
    concept: str
    topics: Optional[List[str]] = None  # List of concepts being studied

class ExplainResponse(BaseModel):
    explanation: str

# Routes

@app.get("/")
async def root():
    """API status and documentation"""
    return {
        "message": "MindPalace Vector DB API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /query": "Query vector DB with RAG",
            "POST /query_raw": "Query vector DB (raw results)",
            "POST /add_pdf": "Add PDF text to vector DB",
            "POST /generate_concepts": "Generate concepts from PDF text",
            "POST /generate_associations": "Generate mnemonic associations",
            "POST /generate_story_associations": "Generate story-based associations with transitions",
            "POST /analyze_room_image": "Analyze room object image with AI",
            "POST /detect_room_objects": "Auto-detect objects in room image",
            "POST /extract_object_image": "Extract object from room image (image-to-image only)",
            "GET /stats/{collection_name}": "Get collection statistics",
            "GET /collections": "List all collections",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vector_db_api"}

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the vector database with RAG (Retrieval-Augmented Generation).
    Returns an AI-generated answer based on retrieved context.
    """
    try:
        # Get RAG answer using the ask() method
        result = rag_service.ask(
            collection_name=request.collection_name,
            question=request.question,
            n_results=request.n_results,
            include_sources=True
        )
        
        # Extract answer and sources
        answer = result.get("answer", "No answer generated")
        sources = result.get("sources", [])
        
        return QueryResponse(answer=answer, sources=sources)
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/query_raw")
async def query_raw(request: QueryRequest):
    """
    Query the vector database directly (no RAG).
    Returns raw documents, distances, and metadata.
    """
    try:
        results = db_manager.query_vector_db(
            collection_name=request.collection_name,
            query=request.question,
            n_results=request.n_results
        )
        
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        
        return {
            "documents": results["documents"],
            "distances": results["distances"],
            "metadatas": results["metadatas"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/add_pdf", response_model=AddPDFResponse)
async def add_pdf(request: AddPDFRequest):
    """
    Add PDF text to the vector database.
    Text will be chunked and embedded automatically.
    """
    try:
        num_chunks = db_manager.add_pdf_to_vector_db(
            collection_name=request.collection_name,
            pdf_text=request.pdf_text,
            pdf_filename=request.pdf_filename,
            metadata=request.metadata
        )
        
        return AddPDFResponse(
            success=True,
            chunks_added=num_chunks,
            message=f"Successfully added {num_chunks} chunks to collection '{request.collection_name}'"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add PDF: {str(e)}")

@app.post("/generate_concepts", response_model=GenerateConceptsResponse)
async def generate_concepts(request: GenerateConceptsRequest):
    """
    Generate key concepts from PDF text using Groq LLM.
    """
    logger.info(f"Received generate_concepts request for {request.num_concepts} concepts")
    try:
        concepts = concept_generator.generate_concepts(
            pdf_text=request.pdf_text,
            num_concepts=request.num_concepts
        )
        
        if isinstance(concepts, dict) and "error" in concepts:
            logger.error(f"Concept generation failed: {concepts['error']}")
            raise HTTPException(status_code=400, detail=concepts["error"])
        
        logger.info(f"Successfully generated {len(concepts)} concepts")
        return GenerateConceptsResponse(concepts=concepts)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate concepts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate concepts: {str(e)}")

@app.post("/generate_associations", response_model=GenerateAssociationsResponse)
async def generate_associations(request: GenerateAssociationsRequest):
    """
    Generate memorable associations between concepts and room objects using Groq LLM.
    """
    logger.info(f"Received generate_associations request for {len(request.concepts)} concepts and {len(request.room_objects)} objects")
    try:
        associations = association_generator.generate_associations(
            concepts=request.concepts,
            room_objects=request.room_objects,
            pdf_text=request.pdf_text
        )
        
        if isinstance(associations, dict) and "error" in associations:
            logger.error(f"Association generation failed: {associations['error']}")
            raise HTTPException(status_code=400, detail=associations["error"])
        
        logger.info(f"Successfully generated {len(associations)} associations")
        return GenerateAssociationsResponse(associations=associations)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate associations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate associations: {str(e)}")

@app.post("/generate_story_associations", response_model=GenerateAssociationsResponse)
async def generate_story_associations(request: GenerateAssociationsRequest):
    """
    Generate story-based memorable associations with transitions between consecutive rows.
    Each association flows naturally into the next, creating a connected narrative.
    """
    logger.info(f"Received generate_story_associations request for {len(request.concepts)} concepts and {len(request.room_objects)} objects")
    try:
        associations = association_generator.generate_story_associations(
            concepts=request.concepts,
            room_objects=request.room_objects,
            pdf_text=request.pdf_text
        )
        
        if isinstance(associations, dict) and "error" in associations:
            logger.error(f"Story association generation failed: {associations['error']}")
            raise HTTPException(status_code=400, detail=associations["error"])
        
        logger.info(f"Successfully generated {len(associations)} story-based associations")
        return GenerateAssociationsResponse(associations=associations)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate story-based associations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate story-based associations: {str(e)}")

@app.get("/stats/{collection_name}", response_model=CollectionStatsResponse)
async def get_stats(collection_name: str):
    """Get statistics about a collection"""
    try:
        stats = db_manager.get_collection_stats(collection_name)
        return CollectionStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/collections")
async def list_collections():
    """List all available collections"""
    try:
        collections = db_manager.client.list_collections()
        return {
            "collections": [
                {
                    "name": col.name,
                    "count": col.count()
                }
                for col in collections
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

@app.post("/explain", response_model=ExplainResponse)
async def explain_concept(request: ExplainRequest):
    """
    Explain a concept or answer a question about the floor's content using RAG.
    This endpoint is used by the chatbot to provide contextual answers.
    """
    logger.info(f"Received explain request for floor {request.floor_id}: {request.concept}")
    if request.topics:
        logger.info(f"Topics context: {request.topics}")
    
    try:
        # Use the floor_id as collection name
        collection_name = f"floor_{request.floor_id}"
        
        # Check if collection exists
        stats = db_manager.get_collection_stats(collection_name)
        logger.info(f"Collection '{collection_name}' stats: {stats}")
        
        if not stats['exists'] or stats['count'] == 0:
            logger.warning(f"Collection '{collection_name}' does not exist or is empty")
            
            # List all available collections for debugging
            try:
                all_collections = db_manager.client.list_collections()
                collection_names = [c.name for c in all_collections]
                logger.info(f"Available collections: {collection_names}")
            except Exception as list_err:
                logger.error(f"Failed to list collections: {list_err}")
            
            return ExplainResponse(
                explanation=f"I don't have any content indexed for this floor yet. Please make sure you've:\n\n1. Uploaded PDF files when creating the floor\n2. Completed the generation process\n3. Waited for the content to be indexed\n\nTry regenerating the floor with PDF files included."
            )
        
        logger.info(f"Querying collection '{collection_name}' with {stats['count']} chunks")
        
        # Enhance the question with topic context for better retrieval
        enhanced_question = request.concept
        if request.topics and len(request.topics) > 0:
            topics_str = ", ".join(request.topics[:5])  # Limit to first 5 topics
            enhanced_question = f"Topics being studied: {topics_str}. Question: {request.concept}"
            logger.info(f"Enhanced query: {enhanced_question}")
        
        # Query the vector database using ask() method with enhanced question
        result = rag_service.ask(
            collection_name=collection_name,
            question=enhanced_question,
            n_results=5,  # Get top 5 most relevant chunks for better context
            include_sources=True  # Enable sources for debugging
        )
        
        answer = result.get("answer", "I couldn't generate an answer.")
        
        # Log retrieved sources for debugging
        if result.get("sources"):
            logger.info(f"Retrieved from sources: {[s.get('source_file') for s in result['sources']]}")
        
        logger.info(f"Generated explanation for '{request.concept}': {len(answer)} chars")
        
        return ExplainResponse(explanation=answer)
        
    except Exception as e:
        logger.error(f"Failed to explain concept: {str(e)}", exc_info=True)
        # Return a helpful error message instead of failing completely
        return ExplainResponse(
            explanation=f"I encountered an error while searching for information about '{request.concept}'.\n\nError: {str(e)}\n\nPlease try:\n1. Rephrasing your question\n2. Checking if the backend server is running\n3. Verifying that PDFs were uploaded successfully"
        )

@app.post("/extract_pdf")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extract text from an uploaded PDF file using Groq Vision API.
    Returns the extracted text and page count.
    """
    logger.info(f"Received PDF extraction request for file: {file.filename}")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"Saved PDF to temporary file: {tmp_path}")
        
        # Extract text using Groq Vision API
        extracted_text = extract_text_with_groq(tmp_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        logger.info("Temporary file deleted")
        
        # Check for errors
        if isinstance(extracted_text, dict) and "error" in extracted_text:
            logger.error(f"PDF extraction failed: {extracted_text['error']}")
            raise HTTPException(status_code=400, detail=extracted_text["error"])
        
        # Count pages (rough estimate from page markers)
        page_count = extracted_text.count("--- Page ") if extracted_text else 0
        
        logger.info(f"Successfully extracted text from {file.filename}: {len(extracted_text)} chars, {page_count} pages")
        
        return {
            "extracted_text": extracted_text,
            "page_count": page_count,
            "message": f"Successfully extracted {page_count} pages"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract PDF: {str(e)}", exc_info=True)
        # Clean up temp file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF: {str(e)}")

@app.post("/analyze_room_image")
async def analyze_room_image(file: UploadFile = File(...)):
    """
    Analyze a room object image using Groq Vision API.
    Returns the object name and description.
    """
    logger.info(f"Received room image analysis request for file: {file.filename}")
    
    try:
        import base64
        import io
        import json
        from PIL import Image
        from groq import Groq
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found")
        
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Resize image for faster processing (max 1024px)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.debug(f"Resized image to {new_size}")
        
        # Convert to RGB if needed (remove alpha channel)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{b64_image}"
        
        logger.info("Image converted to base64, calling Groq Vision API...")
        
        # Call Groq Vision API
        client = Groq(api_key=api_key)
        
        system_prompt = """Sen görüntülerdeki nesneleri tanımlamada uzmansın. 

ÖNEMLİ: Tüm yanıtların TÜRKÇE olmalıdır. İngilizce kelime kullanma.

Görevin görüntüde gösterilen nesneyi tanımlamak ve şunları sağlamak:
1. Kısa, net bir isim (maksimum 2-4 kelime, TÜRKÇE)
2. Kısa bir açıklama (tek cümle, 10-20 kelime, TÜRKÇE)

Spesifik ve öz ol. Bu nesneyi benzersiz veya dikkate değer kılan şeylere odaklan.

TAMAMEN TÜRKÇE JSON formatında yanıt ver:
{
  "name": "Türkçe Kısa Nesne İsmi",
  "description": "Türkçe kısa tek cümlelik açıklama"
}

Örnekler:
- {"name": "Siyah Kalem", "description": "Masa üzerinde duran ince uçlu siyah mürekkepli yazı kalemi"}
- {"name": "Bilgisayar Monitörü", "description": "Geniş ekranlı modern LCD monitör"}"""

        user_prompt = "Bu görüntüde hangi nesne gösteriliyor? Kısa bir Türkçe isim ve kısa Türkçe açıklama ver. SADECE TÜRKÇE yanıt ver, İngilizce kullanma."
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Llama Vision model
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result_text = response.choices[0].message.content
        logger.debug(f"API response: {result_text}")
        
        result = json.loads(result_text)
        
        name = result.get("name", "Unknown Object")
        description = result.get("description", "")
        
        logger.info(f"Successfully analyzed image: {name}")
        
        return {
            "name": name,
            "description": description,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze room image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")


@app.post("/detect_room_objects")
async def detect_room_objects(file: UploadFile = File(...), num_objects: int = 5):
    """
    Detect main objects in a room image using Groq Vision API.
    Returns list of detected objects with names and descriptions.
    """
    logger.info(f"Detecting {num_objects} objects in room image: {file.filename}")
    
    try:
        import base64
        import io
        import json
        from PIL import Image
        from groq import Groq
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found")
        
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Resize for faster processing
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{b64_image}"
        
        logger.info("Calling Groq Vision API to detect objects...")
        
        client = Groq(api_key=api_key)
        
        system_prompt = f"""Sen oda görüntülerini analiz etme ve nesneleri tanımlamada uzmansın.

ÖNEMLİ: Tüm yanıtların TÜRKÇE olmalıdır. İngilizce kelime kullanma.

Bu oda görüntüsünü analiz et ve en belirgin ve farklı {num_objects} nesneyi tanımla.

ÖNEMLİ KURALLAR:
- İNSAN veya kişi YOK
- Mobilya, dekorasyon ve akılda kalıcı eşyalara odaklan
- Net görülebilen ve farklı nesneler seç
- Nesneler hafıza sarayı tekniği için uygun olmalı (akılda kalıcı, sabit)

Her nesne için TÜRKÇE sağla:
1. name: Kısa, net Türkçe isim (2-4 kelime)
2. description: Kısa Türkçe açıklama (tek cümle, 10-20 kelime)

TAMAMEN TÜRKÇE JSON formatında tam olarak {num_objects} nesne döndür:
{{
  "objects": [
    {{"name": "Türkçe Nesne İsmi", "description": "Türkçe kısa açıklama"}},
    ...
  ]
}}

Örnek nesneler (TÜRKÇE):
- {{"name": "Ahşap Masa", "description": "Odanın ortasında duran büyük ahşap çalışma masası"}}
- {{"name": "Yeşil Bitki", "description": "Köşede duran yaprakları geniş saksı bitkisi"}}"""

        user_prompt = f"Bu odadaki iyi hafıza çapaları olacak {num_objects} ana nesneyi TÜRKÇE olarak tanımla. İnsanları hariç tut. Tüm isimler ve açıklamalar TÜRKÇE olmalı. İngilizce kullanma."
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        logger.debug(f"Detected objects: {result_text}")
        
        result = json.loads(result_text)
        objects = result.get("objects", [])
        
        logger.info(f"Successfully detected {len(objects)} objects")
        
        return {
            "objects": objects,
            "count": len(objects),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Failed to detect room objects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to detect objects: {str(e)}")


@app.post("/extract_object_image")
async def extract_object_image(
    room_image: UploadFile = File(...),
    object_name: str = None,
    object_description: str = None
):
    """
    Extract a specific object from room image using fal.ai image-to-image model.
    Uses qwen-image-edit to isolate and extract objects from the room photo.
    Does NOT fallback to text-to-image generation.
    Receives the room image file directly via multipart/form-data.
    
    Args:
        room_image: Room photo file (UploadFile)
        object_name: Name of the object to extract
        object_description: Description of the object
        
    Returns:
        { success: true, image_url: "...", object_name: "..." }
        OR raises HTTPException on failure
    """
    logger.info(f"Extracting object image: {object_name}")
    
    try:
        from fal_service import extract_object_from_room
        import base64
        import io
        from PIL import Image
        
        if not all([object_name, object_description]):
            raise HTTPException(status_code=400, detail="Missing object_name or object_description")
        
        # Read and convert image to base64 data URI
        content = await room_image.read()
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # Convert to base64 data URI
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{b64_image}"
        
        logger.info(f"Room image converted to data URI, size: {len(b64_image)} chars")
        
        # Extract object using image-to-image model only (no fallback to generation)
        result = extract_object_from_room(
            room_image_url=data_url,
            object_name=object_name,
            object_description=object_description
        )
        
        if result.get('success'):
            logger.info(f"Successfully extracted object: {object_name}")
            return result
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Extraction failed for {object_name}: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract object: {error_msg}"
            )
            
    except Exception as e:
        logger.error(f"Failed to extract object image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to extract object: {str(e)}")


# Run server
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting MindPalace Vector DB API Server")
    print("=" * 60)
    print("📍 Server: http://localhost:8081")
    print("📚 Docs: http://localhost:8081/docs")
    print("🔍 Health: http://localhost:8081/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )
