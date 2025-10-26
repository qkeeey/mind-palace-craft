"""
Simple test to verify vector database setup
"""
from vector_db import VectorDBManager

print("=== Testing Vector Database Setup ===\n")

# Initialize the vector DB manager
print("1. Initializing VectorDBManager...")
db_manager = VectorDBManager()
print("✅ VectorDBManager initialized\n")

# Test text
test_text = """
The French Revolution was a period of radical social and political change in France. 
It began in 1789 and ended in the late 1790s with the rise of Napoleon Bonaparte.
The Revolution overthrew the monarchy, established a republic, and saw violent periods 
such as the Reign of Terror.
"""

print("2. Adding test text to vector database...")
collection_name = "test_collection"
num_chunks = db_manager.add_pdf_to_vector_db(
    collection_name=collection_name,
    pdf_text=test_text,
    pdf_filename="test_document",
    metadata={"test": True}
)
print(f"✅ Added {num_chunks} chunks to database\n")

# Test querying
print("3. Testing query...")
results = db_manager.query_vector_db(
    collection_name=collection_name,
    query="What happened during the French Revolution?",
    n_results=2
)
print(f"✅ Found {len(results['documents'])} relevant chunks\n")

print("Query results:")
for i, (doc, dist, meta) in enumerate(zip(results['documents'], results['distances'], results['metadatas']), 1):
    print(f"\n--- Result {i} ---")
    print(f"Text: {doc[:200]}...")
    print(f"Distance: {dist:.4f}")
    print(f"Source: {meta.get('source', 'N/A')}")

# Show stats
stats = db_manager.get_collection_stats(collection_name)
print(f"\n4. Collection stats:")
print(f"   Total chunks: {stats['count']}")

print("\n=== All tests passed! ✅ ===")
