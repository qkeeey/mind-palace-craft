"""
Test script for story-based associations feature
Run this to verify the new feature works correctly
"""

import requests
import json

LOCAL_API_URL = "http://localhost:8081"

def test_story_associations():
    """Test the new story-based associations endpoint"""
    
    print("=" * 60)
    print("Testing Story-Based Associations Feature")
    print("=" * 60)
    
    # Sample data
    concepts = [
        {
            "concept": "Photosynthesis",
            "description": "Process where plants convert light energy into chemical energy"
        },
        {
            "concept": "Cell Membrane",
            "description": "Selective barrier that protects the cell and controls what enters and exits"
        },
        {
            "concept": "DNA Structure",
            "description": "Double helix structure containing genetic information"
        }
    ]
    
    room_objects = [
        {
            "object_name": "desk",
            "short_description": "Wooden desk with drawers and a smooth surface"
        },
        {
            "object_name": "lamp",
            "short_description": "Reading lamp with adjustable arm and bright LED"
        },
        {
            "object_name": "chair",
            "short_description": "Office chair with wheels and adjustable height"
        }
    ]
    
    pdf_text = """
    This chapter covers the fundamental processes of cellular biology.
    Photosynthesis is the process by which plants convert sunlight into energy.
    The cell membrane acts as a gatekeeper, controlling molecular traffic.
    DNA contains the genetic instructions for all living organisms.
    """
    
    # Test the endpoint
    print("\n1. Sending request to /generate_story_associations...")
    print(f"   Concepts: {len(concepts)}")
    print(f"   Objects: {len(room_objects)}")
    
    try:
        response = requests.post(
            f"{LOCAL_API_URL}/generate_story_associations",
            json={
                "concepts": concepts,
                "room_objects": room_objects,
                "pdf_text": pdf_text
            },
            timeout=60
        )
        
        if response.status_code == 200:
            print("   ✅ Request successful!")
            
            data = response.json()
            associations = data.get("associations", [])
            
            print(f"\n2. Generated {len(associations)} story-based associations:")
            print("=" * 60)
            
            for i, assoc in enumerate(associations, 1):
                print(f"\n[Row {i}]")
                print(f"Concept: {assoc['concept']}")
                print(f"Object: {assoc['object_name']}")
                print(f"\nAssociation (with story transition):")
                print(f"{assoc['association']}")
                print("-" * 60)
                
                # Check if transitions exist (except for last item)
                if i < len(associations):
                    # Look for transition keywords
                    text = assoc['association'].lower()
                    has_transition = any(keyword in text for keyword in [
                        'nearby', 'next', 'turning', 'notice', 'see', 'look',
                        'behind', 'beside', 'then', 'as you', 'moving'
                    ])
                    
                    if has_transition:
                        print("✅ Transition detected")
                    else:
                        print("⚠️  No clear transition found (may need improvement)")
                else:
                    print("✅ Last item (no transition needed)")
            
            print("\n" + "=" * 60)
            print("✅ Story-based associations feature is working!")
            print("=" * 60)
            
            # Check association lengths
            print("\n3. Quality Metrics:")
            avg_length = sum(len(a['association']) for a in associations) / len(associations)
            print(f"   Average association length: {avg_length:.0f} characters")
            
            if avg_length < 50:
                print("   ⚠️  Associations might be too short")
            elif avg_length > 300:
                print("   ⚠️  Associations might be too long")
            else:
                print("   ✅ Association length is appropriate")
            
        else:
            print(f"   ❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to API server")
        print("   Make sure the API server is running on http://localhost:8081")
        print("   Run: cd alpaca && python api_server.py")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def test_comparison():
    """Compare regular vs story-based associations"""
    
    print("\n" + "=" * 60)
    print("Comparing Regular vs Story-Based Associations")
    print("=" * 60)
    
    concepts = [
        {"concept": "Mitosis", "description": "Cell division process"},
        {"concept": "Osmosis", "description": "Movement of water across membranes"}
    ]
    
    room_objects = [
        {"object_name": "desk", "short_description": "Wooden desk"},
        {"object_name": "lamp", "short_description": "Reading lamp"}
    ]
    
    try:
        # Test regular associations
        print("\n1. Regular Associations:")
        print("-" * 60)
        regular_response = requests.post(
            f"{LOCAL_API_URL}/generate_associations",
            json={"concepts": concepts, "room_objects": room_objects},
            timeout=60
        )
        
        if regular_response.status_code == 200:
            regular_data = regular_response.json()
            for assoc in regular_data.get("associations", []):
                print(f"• {assoc['object_name']}: {assoc['association']}")
        
        # Test story-based associations
        print("\n2. Story-Based Associations:")
        print("-" * 60)
        story_response = requests.post(
            f"{LOCAL_API_URL}/generate_story_associations",
            json={"concepts": concepts, "room_objects": room_objects},
            timeout=60
        )
        
        if story_response.status_code == 200:
            story_data = story_response.json()
            for assoc in story_data.get("associations", []):
                print(f"• {assoc['object_name']}: {assoc['association']}")
        
        print("\n" + "=" * 60)
        print("Notice how story-based associations flow into each other!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during comparison: {str(e)}")


if __name__ == "__main__":
    print("\n🧪 Story-Based Associations Test Suite\n")
    
    # Run tests
    test_story_associations()
    
    print("\n" + "=" * 60)
    response = input("\nWould you like to compare with regular associations? (y/n): ")
    if response.lower() == 'y':
        test_comparison()
    
    print("\n✅ Testing complete!\n")
