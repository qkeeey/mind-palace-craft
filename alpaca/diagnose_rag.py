"""
RAG System Diagnostic Script
Run this to check if the RAG chatbot system is set up correctly.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    print("\n" + "="*60)
    print("📦 Checking Dependencies")
    print("="*60)
    
    required = [
        'chromadb',
        'sentence_transformers',
        'groq',
        'fastapi',
        'uvicorn',
        'python-dotenv'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} - NOT INSTALLED")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    return True

def check_env_vars():
    """Check if environment variables are set."""
    print("\n" + "="*60)
    print("🔑 Checking Environment Variables")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        print(f"✅ GROQ_API_KEY is set ({api_key[:10]}...)")
        return True
    else:
        print("❌ GROQ_API_KEY not found")
        print("   Add it to alpaca/.env file:")
        print("   GROQ_API_KEY=your_key_here")
        return False

def check_vector_db():
    """Check if vector database is accessible."""
    print("\n" + "="*60)
    print("🗄️  Checking Vector Database")
    print("="*60)
    
    try:
        from vector_db import VectorDBManager
        
        db = VectorDBManager()
        print("✅ VectorDBManager initialized")
        
        # Check for chroma_db directory
        chroma_path = Path("chroma_db")
        if chroma_path.exists():
            print(f"✅ ChromaDB directory exists: {chroma_path.absolute()}")
            files = list(chroma_path.glob("*"))
            print(f"   Contains {len(files)} files")
        else:
            print("⚠️  ChromaDB directory doesn't exist yet (will be created on first use)")
        
        # List collections
        try:
            collections = db.client.list_collections()
            print(f"✅ Found {len(collections)} collections:")
            for col in collections:
                count = col.count()
                print(f"   - {col.name}: {count} chunks")
            
            if not collections:
                print("   ⚠️  No collections yet (create a floor with PDFs to index)")
            
            return True
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing VectorDBManager: {e}")
        return False

def check_rag_service():
    """Check if RAG service is working."""
    print("\n" + "="*60)
    print("🤖 Checking RAG Service")
    print("="*60)
    
    try:
        from rag_service import RAGService
        
        rag = RAGService()
        print("✅ RAGService initialized")
        
        # Check if ask() method exists
        if hasattr(rag, 'ask'):
            print("✅ ask() method exists")
        else:
            print("❌ ask() method not found!")
            return False
        
        # Check if deprecated query() method exists
        if hasattr(rag, 'query'):
            print("⚠️  Deprecated query() method still exists (should use ask())")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing RAGService: {e}")
        return False

def test_collection(collection_name="floor_1"):
    """Test querying a specific collection."""
    print("\n" + "="*60)
    print(f"🔍 Testing Collection: {collection_name}")
    print("="*60)
    
    try:
        from vector_db import VectorDBManager
        from rag_service import RAGService
        
        db = VectorDBManager()
        
        # Check if collection exists
        stats = db.get_collection_stats(collection_name)
        
        if not stats['exists']:
            print(f"⚠️  Collection '{collection_name}' doesn't exist yet")
            print("   Create a floor with PDFs to test the RAG system")
            return False
        
        print(f"✅ Collection exists: {stats['count']} chunks")
        
        # Test query
        print("\n📝 Testing query...")
        test_question = "What is this content about?"
        
        results = db.query_vector_db(collection_name, test_question, n_results=3)
        
        if "error" in results:
            print(f"❌ Query error: {results['error']}")
            return False
        
        print(f"✅ Query successful! Found {len(results['documents'])} results")
        
        if results['documents']:
            print("\n📄 Top result preview:")
            doc = results['documents'][0]
            print(f"   {doc[:200]}...")
            print(f"   Distance: {results['distances'][0]:.4f}")
        
        # Test RAG answer generation
        print("\n🤖 Testing RAG answer generation...")
        rag = RAGService()
        
        result = rag.ask(
            collection_name=collection_name,
            question=test_question,
            n_results=3,
            include_sources=True
        )
        
        if result.get('answer'):
            print("✅ RAG answer generated successfully!")
            print(f"\n💬 Answer preview:")
            answer = result['answer']
            print(f"   {answer[:300]}...")
        else:
            print("❌ No answer generated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api_server():
    """Check if API server can be imported."""
    print("\n" + "="*60)
    print("🚀 Checking API Server")
    print("="*60)
    
    try:
        import api_server
        print("✅ api_server.py can be imported")
        
        # Check if app is defined
        if hasattr(api_server, 'app'):
            print("✅ FastAPI app is defined")
        else:
            print("❌ FastAPI app not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing api_server: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("\n" + "="*60)
    print("🏥 MindPalace RAG System Diagnostics")
    print("="*60)
    
    # Change to alpaca directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    results = {
        "Dependencies": check_dependencies(),
        "Environment Variables": check_env_vars(),
        "Vector Database": check_vector_db(),
        "RAG Service": check_rag_service(),
        "API Server": check_api_server()
    }
    
    # Try to test a collection if available
    from vector_db import VectorDBManager
    db = VectorDBManager()
    collections = db.client.list_collections()
    
    if collections:
        # Test first collection
        collection_name = collections[0].name
        results["Collection Test"] = test_collection(collection_name)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All checks passed! RAG system is ready.")
        print("\nNext steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Create a floor with PDF files")
        print("3. Test the chatbot in the Walkthrough page")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nSee RAG_CHATBOT_DEBUG.md for troubleshooting help.")
    print("="*60)

if __name__ == "__main__":
    main()
