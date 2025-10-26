"""
Clean up ChromaDB collections utility
This script helps manage and clean up old collections in the vector database
"""

import os
import sys
from pathlib import Path

def list_collections():
    """List all collections in ChromaDB."""
    from vector_db import VectorDBManager
    
    print("\n" + "="*60)
    print("📊 ChromaDB Collections")
    print("="*60)
    
    try:
        db = VectorDBManager()
        collections = db.client.list_collections()
        
        if not collections:
            print("No collections found.")
            return []
        
        print(f"\nFound {len(collections)} collection(s):\n")
        
        collection_data = []
        for col in collections:
            count = col.count()
            collection_data.append({
                'name': col.name,
                'count': count
            })
            print(f"  • {col.name}: {count} chunks")
        
        return collection_data
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        return []

def delete_collection(collection_name: str):
    """Delete a specific collection."""
    from vector_db import VectorDBManager
    
    try:
        db = VectorDBManager()
        db.client.delete_collection(name=collection_name)
        print(f"✅ Deleted collection: {collection_name}")
        return True
    except Exception as e:
        print(f"❌ Error deleting collection '{collection_name}': {e}")
        return False

def delete_all_collections():
    """Delete all collections (use with caution!)."""
    from vector_db import VectorDBManager
    
    try:
        db = VectorDBManager()
        collections = db.client.list_collections()
        
        if not collections:
            print("No collections to delete.")
            return
        
        print(f"\n⚠️  About to delete {len(collections)} collection(s):")
        for col in collections:
            print(f"  • {col.name}")
        
        confirm = input("\nAre you sure? Type 'DELETE ALL' to confirm: ")
        if confirm != "DELETE ALL":
            print("❌ Cancelled.")
            return
        
        deleted = 0
        for col in collections:
            try:
                db.client.delete_collection(name=col.name)
                print(f"✅ Deleted: {col.name}")
                deleted += 1
            except Exception as e:
                print(f"❌ Failed to delete {col.name}: {e}")
        
        print(f"\n✅ Deleted {deleted} collection(s).")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def delete_non_floor_collections():
    """Delete collections that don't follow the floor_X pattern."""
    from vector_db import VectorDBManager
    
    try:
        db = VectorDBManager()
        collections = db.client.list_collections()
        
        if not collections:
            print("No collections found.")
            return
        
        # Find collections that don't match floor_{id} pattern
        non_floor_collections = []
        for col in collections:
            if not col.name.startswith('floor_'):
                non_floor_collections.append(col.name)
        
        if not non_floor_collections:
            print("✅ All collections follow the correct naming pattern.")
            return
        
        print(f"\n⚠️  Found {len(non_floor_collections)} collection(s) with non-standard names:")
        for name in non_floor_collections:
            print(f"  • {name}")
        
        confirm = input("\nDelete these collections? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled.")
            return
        
        deleted = 0
        for name in non_floor_collections:
            if delete_collection(name):
                deleted += 1
        
        print(f"\n✅ Deleted {deleted} collection(s).")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_floor_collections():
    """Verify floor collections exist and have data."""
    from vector_db import VectorDBManager
    import re
    
    try:
        db = VectorDBManager()
        collections = db.client.list_collections()
        
        floor_collections = [col for col in collections if col.name.startswith('floor_')]
        
        if not floor_collections:
            print("⚠️  No floor collections found.")
            return
        
        print(f"\n📊 Floor Collections Status:\n")
        
        for col in floor_collections:
            count = col.count()
            match = re.match(r'floor_([a-zA-Z0-9-]+)', col.name)
            floor_id = match.group(1) if match else "unknown"
            
            status = "✅" if count > 0 else "⚠️ "
            print(f"{status} {col.name} (Floor ID: {floor_id}): {count} chunks")
            
            if count == 0:
                print(f"   └─ Empty collection - consider regenerating this floor")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_menu():
    """Interactive menu for collection management."""
    while True:
        print("\n" + "="*60)
        print("🗄️  ChromaDB Collection Manager")
        print("="*60)
        print("\n1. List all collections")
        print("2. Verify floor collections")
        print("3. Delete specific collection")
        print("4. Delete non-floor collections")
        print("5. Delete ALL collections (⚠️  DANGER)")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            list_collections()
        
        elif choice == "2":
            verify_floor_collections()
        
        elif choice == "3":
            collections = list_collections()
            if collections:
                name = input("\nEnter collection name to delete: ").strip()
                delete_collection(name)
        
        elif choice == "4":
            delete_non_floor_collections()
        
        elif choice == "5":
            delete_all_collections()
        
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1-6.")

def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🧹 ChromaDB Collection Cleanup Utility")
    print("="*60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Check if running with arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_collections()
        elif command == "verify":
            verify_floor_collections()
        elif command == "clean":
            delete_non_floor_collections()
        elif command == "delete-all":
            delete_all_collections()
        elif command.startswith("delete:"):
            collection_name = command.split(":", 1)[1]
            delete_collection(collection_name)
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python cleanup_collections.py list          # List all collections")
            print("  python cleanup_collections.py verify        # Verify floor collections")
            print("  python cleanup_collections.py clean         # Delete non-floor collections")
            print("  python cleanup_collections.py delete-all    # Delete ALL collections")
            print("  python cleanup_collections.py delete:<name> # Delete specific collection")
            print("  python cleanup_collections.py               # Interactive menu")
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()
