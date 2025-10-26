import sys
sys.path.insert(0, 'C:/Users/kulni/Metallama/app')

from core_logic import extract_topics, generate_mnemonic_associations
import json

text = """The Greeks 800-300 BC. Early Greek civilization was centered around the Aegean Sea. Between 800 and 300 BC, Greek culture flourished. Colonization occurred from 750 BC around the Mediterranean and Black Sea. Greek society had city-states like Athens and Sparta. Athens developed democracy around 508 BC under Cleisthenes. Sparta maintained a military oligarchy. The Persian Wars occurred 499-449 BC with battles at Marathon, Thermopylae and Salamis. The Peloponnesian War 431-404 BC was between Athens and Sparta, chronicled by Thucydides. Cultural achievements included philosophy (Socrates, Plato, Aristotle), drama (Sophocles, Euripides), and architecture (Parthenon)."""

print("Extracting topics...")
topics = extract_topics(text)
print(f"✅ Extracted {len(topics['topics'])} topics\n")

objects = [
    {"name": "Soldier Figurine", "image": "soldier_figurine.jpg"},
    {"name": "Plant", "image": "plant.jpg"},
    {"name": "Bottle", "image": "bottle.jpg"}
]

print("Generating mnemonics...")
result = generate_mnemonic_associations(topics, objects)
mind_palace = result.get('mind_palace', [])
print(f"✅ Generated {len(mind_palace)} object associations\n")

for i, assoc in enumerate(mind_palace, 1):
    print(f"\n{'='*60}")
    print(f"Association {i}: {assoc['object']}")
    print(f"{'='*60}")
    print(f"Concept Group: {assoc['concept_group']}")
    print(f"Narrative Journey: {assoc['narrative_journey']}")
    print(f"\nConcept Chain ({len(assoc['concept_chain'])} concepts):")
    for j, concept in enumerate(assoc['concept_chain'], 1):
        print(f"\n  {j}. {concept['concept']}")
        print(f"     Location: {concept['location_on_object']}")
        print(f"     Story: {concept['mnemonic_story'][:200]}...")
        if concept.get('sequence_connector'):
            print(f"     → {concept['sequence_connector']}")
