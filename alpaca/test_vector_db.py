"""
Test script to verify vector database setup
"""

from vector_db import VectorDBManager
import os

print("="*60)
print("VECTOR DATABASE TEST")
print("="*60)

# Initialize the manager
print("\n1. Initializing VectorDBManager...")
try:
    db_manager = VectorDBManager()
    print("✅ VectorDBManager initialized successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test text chunking
print("\n2. Testing text chunking...")
sample_text = """
This is a sample text for testing the chunking functionality.
It contains multiple sentences and paragraphs.

The chunking should split this text into smaller, overlapping pieces.
Each chunk should maintain some context from the previous chunk.
This helps with better retrieval during RAG queries.

The system uses semantic boundaries (sentences) to create natural chunks.
"""

try:
    chunks = db_manager.chunk_text(sample_text, chunk_size=100, overlap=20)
    print(f"✅ Created {len(chunks)} chunks from sample text")
    print(f"\nFirst chunk preview: {chunks[0][:80]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test collection creation
print("\n3. Testing collection creation...")
try:
    collection = db_manager.create_collection("test_collection", overwrite=True)
    print("✅ Test collection created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test adding data to vector DB
print("\n4. Testing vector database insertion...")
try:
    test_text = "Machine learning is a subset of artificial intelligence. It uses algorithms to learn from data."
    num_chunks = db_manager.add_pdf_to_vector_db(
        collection_name="test_collection",
        pdf_text=test_text,
        pdf_filename="test.pdf",
        metadata={"test": True}
    )
    print(f"✅ Added {num_chunks} chunks to vector database!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test querying
print("\n5. Testing vector database query...")
try:
    results = db_manager.query_vector_db(
        collection_name="test_collection",
        query="What is machine learning?",
        n_results=2
    )
    print(f"✅ Query successful!")
    print(f"Found {len(results['documents'])} results")
    if results['documents']:
        print(f"\nTop result: {results['documents'][0][:80]}...")
        print(f"Distance: {results['distances'][0]:.4f}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Get stats
print("\n6. Getting collection stats...")
try:
    stats = db_manager.get_collection_stats("test_collection")
    print(f"✅ Collection stats:")
    print(f"   - Name: {stats['name']}")
    print(f"   - Exists: {stats['exists']}")
    print(f"   - Total chunks: {stats['count']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("ALL TESTS PASSED! ✅")
print("="*60)
print("\nThe vector database is ready to use!")
print("Next step: Run 'python pdf_extract.py' to extract and store PDF content")
