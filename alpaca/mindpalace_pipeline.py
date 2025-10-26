"""
Complete MindPalace Generation Pipeline
Handles PDF extraction, concept generation, and association creation
Uses local Groq API key from .env file
"""

import os
import sys
import json
from typing import Dict, List
from dotenv import load_dotenv

from pdf_extract import extract_text_with_groq
from concept_generator import ConceptGenerator
from association_generator import AssociationGenerator
from vector_db import VectorDBManager

# Load environment variables
load_dotenv()


class MindPalacePipeline:
    """Complete pipeline for generating memory palace content."""
    
    def __init__(self):
        """Initialize all services."""
        self.concept_generator = ConceptGenerator()
        self.association_generator = AssociationGenerator()
        self.vector_db = VectorDBManager()
    
    def process_pdf(
        self,
        pdf_path: str,
        collection_name: str,
        room_objects: List[Dict[str, str]],
        num_concepts: int = 10,
        save_outputs: bool = True
    ) -> Dict:
        """
        Complete pipeline: extract PDF → generate concepts → create associations
        
        Args:
            pdf_path: Path to PDF file
            collection_name: Name for vector DB collection
            room_objects: List of room objects with object_name and short_description
            num_concepts: Number of concepts to generate
            save_outputs: Whether to save intermediate outputs to files
            
        Returns:
            Dictionary with extracted_text, concepts, and associations
        """
        result = {}
        
        print("=" * 60)
        print("🏛️  MindPalace Generation Pipeline")
        print("=" * 60)
        
        # Step 1: Extract text from PDF
        print(f"\n📄 Step 1: Extracting text from {os.path.basename(pdf_path)}...")
        extracted_text = extract_text_with_groq(pdf_path)
        
        if extracted_text.startswith("--- ERROR ---"):
            result["error"] = "PDF extraction failed"
            result["details"] = extracted_text
            return result
        
        result["extracted_text"] = extracted_text
        print(f"✅ Extracted {len(extracted_text)} characters")
        
        # Save extracted text
        if save_outputs:
            text_filename = f"pdf_texts/{os.path.basename(pdf_path)}.txt"
            os.makedirs("pdf_texts", exist_ok=True)
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"💾 Saved to {text_filename}")
        
        # Step 2: Add to vector database
        print(f"\n🗄️  Step 2: Adding to vector database (collection: {collection_name})...")
        try:
            num_chunks = self.vector_db.add_pdf_to_vector_db(
                collection_name=collection_name,
                pdf_text=extracted_text,
                pdf_filename=os.path.basename(pdf_path)
            )
            result["chunks_added"] = num_chunks
            print(f"✅ Added {num_chunks} chunks to vector DB")
        except Exception as e:
            print(f"⚠️  Warning: Failed to add to vector DB: {e}")
            result["chunks_added"] = 0
        
        # Step 3: Generate concepts
        print(f"\n🧠 Step 3: Generating {num_concepts} key concepts...")
        concepts = self.concept_generator.generate_concepts(
            pdf_text=extracted_text,
            num_concepts=num_concepts
        )
        
        if isinstance(concepts, dict) and "error" in concepts:
            result["error"] = "Concept generation failed"
            result["details"] = concepts["error"]
            return result
        
        result["concepts"] = concepts
        print(f"✅ Generated {len(concepts)} concepts:")
        for i, concept in enumerate(concepts[:5], 1):  # Show first 5
            print(f"   {i}. {concept['concept']}")
        if len(concepts) > 5:
            print(f"   ... and {len(concepts) - 5} more")
        
        # Save concepts
        if save_outputs:
            concepts_filename = f"pdf_texts/{os.path.basename(pdf_path)}_concepts.json"
            with open(concepts_filename, 'w', encoding='utf-8') as f:
                json.dump(concepts, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to {concepts_filename}")
        
        # Step 4: Generate associations
        print(f"\n🔗 Step 4: Creating memorable associations with room objects...")
        
        # Ensure we have enough room objects
        if len(room_objects) < len(concepts):
            print(f"⚠️  Warning: Only {len(room_objects)} room objects for {len(concepts)} concepts")
            print(f"   Using first {len(room_objects)} concepts")
            concepts = concepts[:len(room_objects)]
        
        associations = self.association_generator.generate_associations(
            concepts=concepts,
            room_objects=room_objects,
            pdf_text=extracted_text[:2000]  # First 2000 chars for context
        )
        
        if isinstance(associations, dict) and "error" in associations:
            result["error"] = "Association generation failed"
            result["details"] = associations["error"]
            return result
        
        result["associations"] = associations
        print(f"✅ Generated {len(associations)} associations:")
        for i, assoc in enumerate(associations[:3], 1):  # Show first 3
            print(f"   {i}. {assoc['concept']} → {assoc['object_name']}")
        if len(associations) > 3:
            print(f"   ... and {len(associations) - 3} more")
        
        # Save associations
        if save_outputs:
            assoc_filename = f"pdf_texts/{os.path.basename(pdf_path)}_associations.json"
            with open(assoc_filename, 'w', encoding='utf-8') as f:
                json.dump(associations, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to {assoc_filename}")
        
        print("\n" + "=" * 60)
        print("✨ Pipeline complete!")
        print("=" * 60)
        
        return result


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python mindpalace_pipeline.py <pdf_path> <collection_name> <room_objects_json> [num_concepts]")
        print("\nExample:")
        print("  python mindpalace_pipeline.py study.pdf my_collection room_objects.json 10")
        print("\nThe room_objects_json should be a JSON file with format:")
        print('  [{"object_name": "...", "short_description": "..."}, ...]')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    collection_name = sys.argv[2]
    objects_file = sys.argv[3]
    num_concepts = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    # Validate inputs
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    if not os.path.exists(objects_file):
        print(f"Error: Room objects file not found: {objects_file}")
        sys.exit(1)
    
    # Load room objects
    with open(objects_file, 'r', encoding='utf-8') as f:
        room_objects = json.load(f)
    
    if not room_objects:
        print("Error: No room objects found in JSON file")
        sys.exit(1)
    
    # Run pipeline
    pipeline = MindPalacePipeline()
    result = pipeline.process_pdf(
        pdf_path=pdf_path,
        collection_name=collection_name,
        room_objects=room_objects,
        num_concepts=num_concepts,
        save_outputs=True
    )
    
    # Check for errors
    if "error" in result:
        print(f"\n❌ Pipeline failed: {result['error']}")
        if "details" in result:
            print(f"   Details: {result['details']}")
        sys.exit(1)
    
    print("\n📊 Summary:")
    print(f"   Text extracted: {len(result['extracted_text'])} characters")
    print(f"   Vector DB chunks: {result['chunks_added']}")
    print(f"   Concepts generated: {len(result['concepts'])}")
    print(f"   Associations created: {len(result['associations'])}")
