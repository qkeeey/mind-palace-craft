"""
RAG (Retrieval-Augmented Generation) Service
Integrates vector database with Groq LLM for intelligent question answering
"""

import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
from vector_db import VectorDBManager

# Load environment variables
load_dotenv()

class RAGService:
    """Service for RAG-based question answering using vector database and Groq."""
    
    def __init__(self, vector_db_manager: VectorDBManager = None):
        """
        Initialize RAG service.
        
        Args:
            vector_db_manager: Existing VectorDBManager instance, or creates new one
        """
        self.db_manager = vector_db_manager or VectorDBManager()
        
        # Initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.groq_client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"  # Fast, powerful model for generation
    
    def retrieve_context(
        self, 
        collection_name: str, 
        query: str, 
        n_results: int = 5
    ) -> tuple[List[str], List[Dict]]:
        """
        Retrieve relevant context from vector database.
        
        Args:
            collection_name: Name of the collection to query
            query: User's question
            n_results: Number of chunks to retrieve
            
        Returns:
            Tuple of (relevant_chunks, metadata)
        """
        print(f"[RAG] Querying collection: {collection_name}")
        print(f"[RAG] Query: {query}")
        
        results = self.db_manager.query_vector_db(
            collection_name=collection_name,
            query=query,
            n_results=n_results
        )
        
        if "error" in results:
            print(f"[RAG] ERROR: {results['error']}")
            return [], []
        
        documents = results['documents']
        metadatas = results['metadatas']
        
        # Log what was retrieved for debugging
        print(f"[RAG] Retrieved {len(documents)} chunks")
        if documents and len(documents) > 0:
            print(f"[RAG] First chunk preview: {documents[0][:150]}...")
            print(f"[RAG] Source: {metadatas[0].get('source', 'Unknown')}")
        
        return documents, metadatas
    
    def generate_answer(
        self, 
        question: str, 
        context_chunks: List[str],
        system_prompt: str = None
    ) -> str:
        """
        Generate answer using Groq LLM with retrieved context.
        
        Args:
            question: User's question
            context_chunks: Retrieved relevant text chunks
            system_prompt: Optional custom system prompt
            
        Returns:
            Generated answer
        """
        if not context_chunks:
            return "I couldn't find relevant information to answer your question."
        
        # Combine context chunks
        context = "\n\n---\n\n".join(context_chunks)
        
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a knowledgeable tutor that provides accurate, direct answers based on the given context.

Your responsibilities:
1. Answer questions using ONLY information from the provided context
2. Be factual, clear, and concise
3. If the answer is not in the context, state that clearly
4. Do not create mnemonics, acronyms, memory devices, or associations
5. Do not make up information or add extra elaboration not supported by the context
6. Answer the specific question asked without tangential information"""
        
        # Construct the prompt
        user_prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer the question directly using only the information in the context above."""
        
        try:
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Very low temperature for factual, consistent responses
                max_tokens=800,   # Shorter responses to avoid rambling
                top_p=0.9        # Reduce randomness
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def ask(
        self, 
        collection_name: str, 
        question: str, 
        n_results: int = 5,
        include_sources: bool = True
    ) -> Dict:
        """
        Complete RAG pipeline: retrieve context and generate answer.
        
        Args:
            collection_name: Name of the vector DB collection
            question: User's question
            n_results: Number of context chunks to retrieve
            include_sources: Whether to return source information
            
        Returns:
            Dictionary with answer and optional source information
        """
        print(f"\n=== RAG Query ===")
        print(f"Question: {question}")
        print(f"Collection: {collection_name}")
        
        # Step 1: Retrieve relevant context
        print("Retrieving relevant context...")
        context_chunks, metadatas = self.retrieve_context(
            collection_name=collection_name,
            query=question,
            n_results=n_results
        )
        
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base. Please make sure PDFs have been uploaded and processed.",
                "sources": []
            }
        
        print(f"Retrieved {len(context_chunks)} relevant chunks")
        
        # Step 2: Generate answer
        print("Generating answer...")
        answer = self.generate_answer(question, context_chunks)
        
        result = {"answer": answer}
        
        # Add source information if requested
        if include_sources:
            sources = []
            for chunk, metadata in zip(context_chunks[:3], metadatas[:3]):  # Top 3 sources
                sources.append({
                    "text_preview": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                    "source_file": metadata.get('source', 'Unknown'),
                    "chunk_index": metadata.get('chunk_index', 0)
                })
            result["sources"] = sources
        
        print("✅ Answer generated successfully")
        return result
    
    def get_explanation_with_mnemonic(
        self, 
        collection_name: str, 
        concept: str
    ) -> str:
        """
        Get a mnemonic-enhanced explanation of a concept.
        Similar to the /explain endpoint in the app API.
        
        Args:
            collection_name: Vector DB collection name
            concept: Concept to explain
            
        Returns:
            Mnemonic-enhanced explanation
        """
        # Custom system prompt for mnemonic explanations
        mnemonic_prompt = """You are a Master Mnemonist and memory champion expert.

Your task: Explain concepts using powerful mnemonic techniques:
1. Create vivid, bizarre, memorable imagery
2. Use acronyms and acrostics when helpful
3. Link to familiar objects or places
4. Make abstract concepts concrete and visual
5. Use the Method of Loci when appropriate

Format your explanation as:
- Brief accurate explanation (2-3 sentences)
- Mnemonic device or memory aid
- Why this mnemonic works

Keep it engaging and memorable!"""
        
        context_chunks, _ = self.retrieve_context(
            collection_name=collection_name,
            query=concept,
            n_results=5
        )
        
        if not context_chunks:
            return f"I couldn't find information about '{concept}' in the knowledge base."
        
        question = f"Explain the concept of '{concept}' with a memorable mnemonic device."
        return self.generate_answer(question, context_chunks, system_prompt=mnemonic_prompt)


# Example usage
if __name__ == "__main__":
    # Initialize RAG service
    rag = RAGService()
    
    # Test with a collection (assumes you've run pdf_extract.py first)
    collection_name = "mind_palace_pdfs"
    
    # Check if collection exists
    stats = rag.db_manager.get_collection_stats(collection_name)
    if not stats['exists']:
        print(f"Collection '{collection_name}' doesn't exist.")
        print("Please run pdf_extract.py first to populate the vector database.")
    else:
        print(f"Collection '{collection_name}' has {stats['count']} chunks")
        
        # Test query
        print("\n" + "="*60)
        test_question = "What is RISC-V?"
        result = rag.ask(
            collection_name=collection_name,
            question=test_question,
            include_sources=True
        )
        
        print(f"\n📚 Question: {test_question}")
        print(f"\n💡 Answer:\n{result['answer']}")
        
        if result.get('sources'):
            print(f"\n📄 Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n{i}. From: {source['source_file']} (chunk {source['chunk_index']})")
                print(f"   Preview: {source['text_preview']}")
        
        # Test mnemonic explanation
        print("\n" + "="*60)
        concept = "RISC-V architecture"
        explanation = rag.get_explanation_with_mnemonic(collection_name, concept)
        print(f"\n🧠 Mnemonic Explanation for '{concept}':")
        print(explanation)
