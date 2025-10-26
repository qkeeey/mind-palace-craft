"""
Vector Database Manager for Mind Palace RAG System
Uses ChromaDB for persistent vector storage with proper chunking and embeddings.
"""

import os
import re
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VectorDBManager:
    """Manages vector database operations for PDF text storage and retrieval."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector database manager.
        
        Args:
            persist_directory: Directory where ChromaDB will persist data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model (using a lightweight, efficient model)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded successfully.")
        
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Args:
            text: The text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split by sentences first for better semantic boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk_size and we have content
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap (last few words)
                words = current_chunk.split()
                overlap_text = ' '.join(words[-overlap:]) if len(words) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def sanitize_collection_name(name: str) -> str:
        """
        Sanitize collection name to meet ChromaDB requirements.
        ChromaDB collection names must:
        - Contain 3-63 characters
        - Start and end with alphanumeric character
        - Contain only alphanumeric, underscores, hyphens
        
        Args:
            name: Raw collection name
            
        Returns:
            Sanitized collection name
        """
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        # Ensure it starts with alphanumeric
        if sanitized and not sanitized[0].isalnum():
            sanitized = 'c' + sanitized
        
        # Ensure it ends with alphanumeric
        if sanitized and not sanitized[-1].isalnum():
            sanitized = sanitized + '0'
        
        # Ensure minimum length
        if len(sanitized) < 3:
            sanitized = sanitized + '_col'
        
        # Ensure maximum length
        if len(sanitized) > 63:
            sanitized = sanitized[:63]
            # Make sure it still ends with alphanumeric after truncation
            if not sanitized[-1].isalnum():
                sanitized = sanitized[:-1] + '0'
        
        return sanitized
    
    def create_collection(self, collection_name: str, overwrite: bool = False):
        """
        Create or get a collection in ChromaDB.
        
        Args:
            collection_name: Name for the collection (e.g., 'floor_1_pdfs')
            overwrite: If True, delete existing collection and create new one
            
        Returns:
            ChromaDB collection object
        """
        # Sanitize collection name (ChromaDB requires specific format)
        original_name = collection_name
        collection_name = self.sanitize_collection_name(collection_name)
        
        if original_name != collection_name:
            print(f"Collection name sanitized: '{original_name}' → '{collection_name}'")
        
        if overwrite:
            try:
                self.client.delete_collection(name=collection_name)
                print(f"Deleted existing collection: {collection_name}")
            except:
                pass
        
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        print(f"Collection '{collection_name}' ready.")
        return collection
    
    def add_pdf_to_vector_db(
        self, 
        collection_name: str, 
        pdf_text: str, 
        pdf_filename: str,
        metadata: Dict = None
    ):
        """
        Process PDF text, chunk it, generate embeddings, and store in vector DB.
        
        Args:
            collection_name: Name of the collection to store in
            pdf_text: Extracted text from the PDF
            pdf_filename: Name of the source PDF file
            metadata: Optional additional metadata to store
        """
        print(f"\n=== Adding PDF to Vector DB ===")
        print(f"PDF: {pdf_filename}")
        print(f"Collection: {collection_name}")
        print(f"Text length: {len(pdf_text)} characters")
        
        # Get or create collection
        collection = self.create_collection(collection_name)
        
        # Chunk the text
        print("Chunking text...")
        chunks = self.chunk_text(pdf_text)
        print(f"Created {len(chunks)} chunks")
        
        # Generate embeddings for all chunks
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=True)
        
        # Prepare metadata for each chunk
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            meta = {
                "source": pdf_filename,
                "chunk_index": i,
                "chunk_size": len(chunk),
                **(metadata or {})
            }
            chunk_metadata.append(meta)
        
        # Generate unique IDs for chunks
        ids = [f"{pdf_filename}_chunk_{i}" for i in range(len(chunks))]
        
        # Add to ChromaDB
        print("Storing in vector database...")
        collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=chunk_metadata,
            ids=ids
        )
        
        print(f"✅ Successfully added {len(chunks)} chunks to vector database")
        
        # Persist the database (with new API, it auto-persists)
        print("✅ Database persisted to disk")
        
        return len(chunks)
    
    def query_vector_db(
        self, 
        collection_name: str, 
        query: str, 
        n_results: int = 5
    ) -> Dict:
        """
        Query the vector database for relevant chunks.
        
        Args:
            collection_name: Name of the collection to query
            query: The search query
            n_results: Number of results to return
            
        Returns:
            Dictionary containing documents, distances, and metadata
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except:
            return {
                "error": f"Collection '{collection_name}' not found",
                "documents": [],
                "distances": [],
                "metadatas": []
            }
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Query the database
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        return {
            "documents": results['documents'][0],
            "distances": results['distances'][0],
            "metadatas": results['metadatas'][0]
        }
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics about a collection."""
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "exists": True
            }
        except:
            return {
                "name": collection_name,
                "count": 0,
                "exists": False
            }


# Example usage
if __name__ == "__main__":
    # Initialize the vector database manager
    db_manager = VectorDBManager()
    
    # Example: Load a PDF text file and add to vector DB
    pdf_text_path = "pdf_texts/RISCV_CALL.txt"
    
    if os.path.exists(pdf_text_path):
        print(f"Loading text from {pdf_text_path}...")
        with open(pdf_text_path, 'r', encoding='utf-8') as f:
            pdf_text = f.read()
        
        # Add to vector database
        collection_name = "floor_1_pdfs"
        db_manager.add_pdf_to_vector_db(
            collection_name=collection_name,
            pdf_text=pdf_text,
            pdf_filename="RISCV_CALL.pdf",
            metadata={"floor_id": 1, "upload_date": "2025-10-25"}
        )
        
        # Query example
        print("\n=== Testing Query ===")
        query = "What is RISC-V?"
        results = db_manager.query_vector_db(collection_name, query, n_results=3)
        
        print(f"\nQuery: {query}")
        print(f"Found {len(results['documents'])} results:\n")
        for i, (doc, distance) in enumerate(zip(results['documents'], results['distances'])):
            print(f"Result {i+1} (distance: {distance:.4f}):")
            print(doc[:200] + "...\n")
        
        # Get collection stats
        stats = db_manager.get_collection_stats(collection_name)
        print(f"\nCollection Stats: {stats}")
    else:
        print(f"Error: {pdf_text_path} not found. Please run pdf_extract.py first.")
