"""
Test script for Memoria API with Greek history content
"""
import requests
import json
import time

# API base URL
API_URL = "http://localhost:5000"

# Greek history text (from previous conversation)
GREEK_HISTORY_TEXT = """
The Greeks 800-300 BC

Early Greek civilization was centered around the Aegean Sea. Between 800 and 300 BC, Greek culture flourished and made lasting contributions to Western civilization.

Colonization and Expansion
From about 750 BC, the Greeks began establishing colonies around the Mediterranean and Black Sea coasts. This colonization was driven by overpopulation, land hunger, and the search for trade opportunities. Major colonies were established in Sicily, southern Italy (Magna Graecia), the Black Sea region, and along the coasts of modern-day France and Spain.

City-States and Political Development
Greek society was organized into independent city-states, or poleis. Each polis had its own government, laws, and military. The two most powerful were Athens and Sparta. Athens developed the world's first democracy around 508 BC under Cleisthenes, where male citizens could participate in government. Sparta, by contrast, maintained a rigid military oligarchy focused on warfare and discipline.

The Persian Wars
Between 499-449 BC, the Greek city-states faced invasion from the Persian Empire. Key battles included Marathon (490 BC), where Athenians defeated a much larger Persian force, and Thermopylae and Salamis (480 BC), where Greek forces, led by Sparta and Athens respectively, repelled Persian invasions. These victories preserved Greek independence and allowed their culture to flourish.

The Peloponnesian War
From 431-404 BC, Athens and Sparta fought for supremacy in Greece. This devastating conflict weakened both powers and eventually led to Spartan victory. However, the war exhausted the Greek city-states and left them vulnerable to outside conquest. The conflict was chronicled by the historian Thucydides, who analyzed the causes and consequences of the war.

Cultural Achievements
This period saw remarkable achievements in philosophy (Socrates, Plato, Aristotle), drama (Sophocles, Euripides, Aristophanes), history (Herodotus, Thucydides), and science (Pythagoras, Hippocrates). The Greeks also excelled in architecture, as evidenced by the Parthenon in Athens, and sculpture, creating idealized representations of the human form.
"""

print("=" * 70)
print("🏛️  MEMORIA API TEST - Greek History")
print("=" * 70)

# Test 1: Upload "PDF" (simulate with text)
print("\n📄 Test 1: Uploading Greek History Text...")
print("-" * 70)

# We'll use session to maintain cookies
session = requests.Session()

# Since we can't actually upload PDF in this test, let's directly test the core logic
# by importing it
import sys
sys.path.insert(0, 'C:/Users/kulni/Metallama/app')
from core_logic import extract_topics, generate_mnemonic_associations, create_vector_store, explain_concept_with_rag, generate_narrative_chain

print("✅ Text loaded")
print(f"   Character count: {len(GREEK_HISTORY_TEXT)}")

# Test 2: Extract Topics
print("\n📊 Test 2: Extracting Topics with Llama...")
print("-" * 70)

try:
    topics = extract_topics(GREEK_HISTORY_TEXT)
    print("✅ Topics extracted successfully!")
    print(f"\n{json.dumps(topics, indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 3: Generate Mnemonic Associations
print("\n🧠 Test 3: Generating Mnemonic Associations...")
print("-" * 70)

objects = [
    {"name": "Soldier Figurine", "image": "soldier_figurine.jpg", "description": "A small ancient Greek warrior statue"},
    {"name": "Plant", "image": "plant.jpg", "description": "A green potted plant on the desk"},
    {"name": "Bottle", "image": "bottle.jpg", "description": "A water bottle"},
    {"name": "Hanging Sign", "image": "hanging_sign.jpg", "description": "A decorative sign on the wall"}
]

try:
    associations = generate_mnemonic_associations(topics, objects)
    print("✅ Mnemonic associations generated!")
    print(f"\nGenerated {len(associations)} associations:")
    
    for i, assoc in enumerate(associations, 1):
        print(f"\n{i}. Object: {assoc['object_name']}")
        print(f"   Topic: {assoc['main_topic']}")
        print(f"   Subtopics: {', '.join(assoc['subtopics'][:3])}...")
        print(f"   Mnemonic Preview: {assoc['mnemonic_story'][:150]}...")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Create Vector Store
print("\n💾 Test 4: Creating Vector Store for RAG...")
print("-" * 70)

palace_id = "test_greek_history"
try:
    create_vector_store(palace_id, GREEK_HISTORY_TEXT)
    print("✅ Vector store created!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 5: RAG Explain Concept
print("\n🔍 Test 5: Testing RAG - Explaining 'Peloponnesian War'...")
print("-" * 70)

try:
    explanation = explain_concept_with_rag(palace_id, "Peloponnesian War")
    print("✅ RAG explanation generated!")
    print(f"\n{explanation}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 6: Generate Narrative Chain
print("\n📖 Test 6: Generating Complete Narrative Story...")
print("-" * 70)

palace_data = {
    "floor_name": "Greek History 800-300 BC",
    "room_id": 1,
    "associations": associations
}

try:
    narrative = generate_narrative_chain(palace_data)
    print("✅ Narrative story generated!")
    print(f"\n{narrative}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print(f"""
Summary:
- Topics extracted: {len(topics['topics'])}
- Mnemonic associations: {len(associations)}
- Vector store chunks: Created
- RAG explanation: Working
- Narrative chain: Generated

Your Memoria API is ready for the hackathon! 🚀
""")
