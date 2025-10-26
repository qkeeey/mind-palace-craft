from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from core_logic import (
    extract_topics, 
    generate_mnemonic_associations,
    create_vector_store,
    explain_concept_with_rag,
    generate_narrative_chain
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Lovable frontend
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'a-secret-key-for-hackathon' # Needed for session management
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory database for the hackathon
db = {
    "floors": [],
    "rooms": [
        {
            "id": 1,
            "name": "Ideal Study Room",
            "objects": ["Desk Lamp", "Bookshelf", "Window", "Potted Plant", "Computer Monitor", "Chair", "Wall Clock", "Wastebasket", "Pen Holder", "Keyboard", "Mouse", "Notebook"]
        }
    ]
}
next_floor_id = 1

@app.route('/')
def index():
    """Renders the main page with the history of mind palaces (floors)."""
    return render_template('index.html', floors=db["floors"])

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """Handles PDF file uploads and stores extracted text in the user's session."""
    if 'files[]' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files[]')
    text_content = ""
    
    for file in files:
        if file.filename == '':
            continue
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                with fitz.open(filepath) as doc:
                    for page in doc:
                        text_content += page.get_text()
            except Exception as e:
                return jsonify({"error": f"Failed to process PDF {filename}: {e}"}), 500

    session['pdf_text'] = text_content
    return jsonify({"message": "Files uploaded and processed successfully.", "char_count": len(text_content)})

@app.route('/setup')
def setup_page():
    """Renders the page for setting up a new mind palace."""
    if 'pdf_text' not in session or not session['pdf_text']:
        # Redirect or show error if no PDF has been uploaded
        return "Please upload PDF files first.", 400
    return render_template('setup.html', rooms=db["rooms"])

@app.route('/generate_palace', methods=['POST'])
def generate_palace():
    """The core logic for generating the mind palace."""
    global next_floor_id
    data = request.get_json()
    floor_name = data.get('floor_name')
    room_id = int(data.get('room_id'))
    
    selected_room = next((room for room in db["rooms"] if room["id"] == room_id), None)
    if not selected_room:
        return jsonify({"error": "Room not found"}), 404
        
    pdf_text = session.get('pdf_text')
    if not pdf_text:
        return jsonify({"error": "No PDF text found in session. Please upload PDFs first."}), 400

    # --- Call Llama-powered core logic ---
    topics = extract_topics(pdf_text)
    if not topics or "topics" not in topics:
        return jsonify({"error": "Failed to extract topics from the text."}), 500

    mind_palace_data = generate_mnemonic_associations(topics, selected_room["objects"])
    if not mind_palace_data or "mind_palace" not in mind_palace_data:
        return jsonify({"error": "Failed to generate the mind palace."}), 500

    # --- Create a new floor and save to our 'database' ---
    new_floor = {
        "id": next_floor_id,
        "name": floor_name,
        "rooms": [
            {
                "id": selected_room["id"],
                "name": selected_room["name"],
                "palace_data": mind_palace_data
            }
        ]
    }
    db["floors"].append(new_floor)
    
    # --- RAG: Create Vector Store for the new palace ---
    create_vector_store(palace_id=new_floor["id"], text=pdf_text)

    next_floor_id += 1
    session.pop('pdf_text', None) # Clear the text from session

    return jsonify({"success": True, "floor_id": new_floor["id"]})

@app.route('/palace/<int:floor_id>')
def view_palace(floor_id):
    """Displays the generated mind palace table for a floor."""
    floor = next((f for f in db["floors"] if f["id"] == floor_id), None)
    if not floor:
        return "Floor not found", 404
    # For simplicity, we'll show the first room's palace
    palace = floor["rooms"][0]["palace_data"]["mind_palace"]
    return render_template('palace.html', floor=floor, palace=palace)

@app.route('/walkthrough/<int:floor_id>/<int:room_id>')
def walkthrough(floor_id, room_id):
    """Displays the walkthrough/slideshow for a specific room in a floor."""
    floor = next((f for f in db["floors"] if f["id"] == floor_id), None)
    if not floor: return "Floor not found", 404
    
    room = next((r for r in floor["rooms"] if r["id"] == room_id), None)
    if not room: return "Room not found", 404

    slides = []
    for concept_group in room["palace_data"]["mind_palace"]:
        for assoc in concept_group["sub_associations"]:
            object_name = concept_group["object"]
            slides.append({
                "main_concept": concept_group["concept"],
                "object": object_name,
                "sub_concept": assoc["sub_concept"],
                "location": assoc["location_on_object"],
                "story": assoc["mnemonic_story"],
                "image_url": f"/static/images/{object_name.lower().replace(' ', '_')}.jpg" 
            })
            
    return render_template('walkthrough.html', floor_name=floor["name"], room_name=room["name"], slides=slides)

# --- NEW API ENDPOINTS FOR ADVANCED FEATURES ---

@app.route('/explain', methods=['POST'])
def explain_concept():
    """RAG endpoint to explain a concept."""
    data = request.get_json()
    floor_id = data.get('floor_id')
    concept = data.get('concept')
    if not all([floor_id, concept]):
        return jsonify({"error": "Missing floor_id or concept"}), 400
        
    explanation = explain_concept_with_rag(floor_id, concept)
    return jsonify({"explanation": explanation})

@app.route('/narrative', methods=['POST'])
def get_narrative():
    """Endpoint to generate a narrative chain for a room."""
    data = request.get_json()
    floor_id = data.get('floor_id')
    room_id = data.get('room_id')

    floor = next((f for f in db["floors"] if f["id"] == floor_id), None)
    if not floor: return jsonify({"error": "Floor not found"}), 404
    
    room = next((r for r in floor["rooms"] if r["id"] == room_id), None)
    if not room: return jsonify({"error": "Room not found"}), 404

    narrative = generate_narrative_chain(room["palace_data"])
    return jsonify({"narrative": narrative})

if __name__ == '__main__':
    app.run(debug=True)
