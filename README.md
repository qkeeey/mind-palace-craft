# Mind Palace - AI-Powered Memory Enhancement System

An intelligent web application that transforms learning materials into memorable experiences using the ancient Memory Palace technique, enhanced by modern AI.

## 🎯 The Problem

The Memory Palace technique is proven effective by top memory competitors, but requires significant creativity and mental effort. Most learners struggle to create vivid associations and structured mental spaces on their own.

## 💡 Our Solution

Mind Palace uses AI to automate the creative heavy-lifting, making this powerful memorization technique accessible to everyone. Simply upload your study materials, and our system generates a complete memory palace with vivid, memorable associations.

## 🏗️ How It Works

1. **Upload PDFs** - Add your study materials (textbooks, notes, papers)
2. **Create Rooms** - Upload room photos or auto-detect objects from images
3. **AI Generation** - System creates associations between room objects and concepts
4. **Study & Review** - Walk through your memory palace with interactive visualizations

## 🌟 Key Features

### Pages & Interfaces
- **Home Dashboard** - View and manage all your memory palaces (floors)
- **Configure Floor** - Upload PDFs, select rooms, generate associations
- **Table View** - Review all object-concept pairs with mnemonic associations
- **3D Walkthrough** - Interactive first-person exploration of your memory palace
- **AI Chatbot** - Ask questions about your study materials with RAG-powered answers

### AI Technologies Used

| Technology | Model/Tool | Purpose |
|------------|------------|---------|
| **Vision AI** | Llama 4 Vision (Groq) | Analyze room images, detect objects, generate labels |
| **Language AI** | Llama 4 17B (Groq) | Create mnemonic associations, concept extraction |
| **Image Generation** | Qwen Image Edit (fal.ai) | Extract individual objects from room photos |
| **OCR** | PyMuPDF + Groq Vision | Extract text and concepts from PDF documents |
| **RAG System** | ChromaDB + Sentence Transformers | Semantic search for chatbot Q&A |
| **Embeddings** | all-MiniLM-L6-v2 | Vector embeddings for concept similarity |

### Core Techniques

- **Prompt Engineering** - Crafted prompts for Turkish output, story-based associations (4-6 sentences), vivid imagery
- **RAG (Retrieval Augmented Generation)** - Context-aware answers using vector similarity search
- **OCR + Vision** - Hybrid approach: PyMuPDF for text extraction, Groq Vision for complex documents
- **Story Chaining** - Sequential associations that flow naturally from one object to the next
- **Multi-modal AI** - Combines text, images, and spatial relationships for enhanced memory

## 🛠️ Tech Stack

**Frontend**: React, TypeScript, Three.js, TailwindCSS  
**Backend**: FastAPI (Python), Supabase (PostgreSQL)  
**AI Infrastructure**: Groq API, fal.ai, ChromaDB, HuggingFace Transformers  

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase account
- Groq API key
- fal.ai API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mind-palace-craft.git
cd mind-palace-craft

# Frontend setup
npm install
npm run dev

# Backend setup
cd alpaca
pip install -r requirements.txt
python api_server.py

