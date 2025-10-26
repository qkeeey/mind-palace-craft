# 🏰 Mind Palace Craft

**Transform your study materials into unforgettable visual memories using AI-powered Memory Palace technique**

Mind Palace Craft is an innovative web application that revolutionizes the way you study and memorize information. By combining the ancient Memory Palace (Method of Loci) technique with modern AI technology, it creates vivid, personalized associations between your study concepts and familiar room objects, making complex information easier to remember and recall.

---

## 📖 Table of Contents

- [The Idea](#-the-idea)
- [Key Features](#-key-features)
- [Screenshots & UI Overview](#-screenshots--ui-overview)
- [Pages & Functionality](#-pages--functionality)
- [How It Works](#-how-it-works)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 The Idea

### The Memory Palace Technique

The **Memory Palace** (or Method of Loci) is an ancient mnemonic technique used by memory champions worldwide. The core principle is simple:
1. Visualize a familiar physical space (like your room)
2. Place pieces of information at specific locations in that space
3. Mentally "walk through" the space to recall the information

### Our Innovation

Mind Palace Craft automates and enhances this technique using AI:
- **AI Vision** analyzes your room photos and identifies memorable objects
- **AI Generation** creates vivid, personalized associations between your study concepts and room objects
- **Turkish Language Support** for native Turkish speakers to learn more naturally
- **Visual Walkthrough** helps you mentally navigate through your memory palace

Instead of manually creating associations, our AI generates **detailed, 4-6 sentence associations in Turkish** that engage multiple senses, use humor and absurdity, and create lasting memories.

---

## ✨ Key Features

### 🤖 AI-Powered Object Detection
- Upload room photos and AI automatically detects memorable objects
- Supports up to 10 objects per room
- Turkish object naming for natural comprehension

### 📚 PDF to Concepts Extraction
- Upload study PDFs (textbooks, notes, articles)
- AI extracts key concepts and descriptions automatically
- Stores concepts in vector database for intelligent retrieval

### 🎨 Vivid Association Generation
- AI creates 4-6 sentence associations in Turkish
- Multiple modes: Standard and Story-based (with transitions)
- Engaging, memorable content using sensory details and humor

### 🚶 Interactive Walkthrough
- Visual journey through your memory palace
- See object images and their associations in sequence
- Story-based flow with smooth transitions

### 📊 Floor Management
- Organize concepts by floors (topics/chapters)
- Multiple rooms per floor
- Easy configuration and reconfiguration

### 🔍 Smart History & Analytics
- Track what you've learned
- Review past associations
- Monitor study progress

---

## 🖼️ Screenshots & UI Overview

### Modern, Clean Interface
- **Dark/Light Theme**: Comfortable viewing in any lighting
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use sidebar and page structure
- **Visual Feedback**: Toasts, loading states, and progress indicators

### Color Scheme
- **Primary**: Blue accent colors for interactive elements
- **Background**: Clean white/dark backgrounds
- **Cards**: Elevated card design with subtle shadows
- **Accent**: Green for success, red for errors, yellow for warnings

---

## 📄 Pages & Functionality

### 1. **Home Page** (`/`)
**Purpose**: Landing page and main dashboard

**Features**:
- Welcome message and app introduction
- Quick access to main features
- Recent activity overview
- Getting started guide for new users

**What You See**:
- Hero section with app tagline
- Feature highlights
- Call-to-action buttons

---

### 2. **PDFs Page** (`/pdfs`)
**Purpose**: Upload and manage study materials

**Features**:
- Upload PDF files (textbooks, notes, articles)
- View list of uploaded PDFs
- Extract text from PDFs using AI
- Generate concepts from PDF content
- Delete PDFs when no longer needed

**What You Do**:
1. Click "Add PDF" button
2. Upload your study material
3. AI processes PDF and extracts text
4. Click "Generate Concepts" to create study concepts
5. View concepts extracted from each PDF

**UI Elements**:
- PDF cards showing title, upload date, page count
- "Generate Concepts" button per PDF
- Delete button for cleanup
- Progress indicators during upload

---

### 3. **Concepts Page** (`/concepts`)
**Purpose**: View and manage extracted study concepts

**Features**:
- Browse all concepts extracted from PDFs
- Filter by PDF source
- Search concepts by keyword
- View concept descriptions
- See which concepts are already associated with rooms

**What You See**:
- Grid of concept cards
- Each card shows:
  - Concept name (Turkish)
  - Description
  - Source PDF
  - Association status

**Actions Available**:
- Search and filter concepts
- View concept details
- Track which concepts have been memorized

---

### 4. **Rooms Page** (`/rooms`)
**Purpose**: Create and manage your memory palace rooms

**Features**:
- Create new rooms with custom names
- Upload room photos
- **Auto-detect objects**: AI automatically identifies 10 objects in your room
- Manual object upload option
- Edit room details
- Delete rooms

**What You Do**:
1. Click "New Room" button
2. Enter room name (e.g., "Study Room", "Bedroom")
3. Upload room photo (optional)
4. Enable "Auto-detect objects" checkbox
5. Set number of objects (2-10)
6. Click "Detect Objects"
7. AI analyzes room and shows Turkish object names
8. AI extracts individual object images
9. Save room with all objects

**Auto-Detect Process**:
- Phase 1: "Analyzing room with Llama 4 vision model..." (3 seconds)
- Shows detected objects: "Siyah kalem, Bilgisayar monitörü, Bilgisayar faresi..."
- Phase 2: "Processing with Qwen image edit model..." (24 seconds)
- All object images appear simultaneously

**UI Elements**:
- Room cards with preview images
- Object count badge
- Edit/Delete buttons
- New Room modal with auto-detect option

---

### 5. **Floors Page** (`/floors`)
**Purpose**: Organize your memory palace by floors (topics)

**Features**:
- Create multiple floors (e.g., "Chapter 1", "Physics", "History")
- Assign PDFs to floors
- View floor statistics
- Navigate to floor details

**What You Do**:
1. Click "New Floor" button
2. Enter floor name (topic/chapter name)
3. Select PDF to associate with floor
4. Save floor
5. Click floor card to view details

**What You See**:
- Grid of floor cards
- Each floor shows:
  - Floor name
  - Associated PDF
  - Number of concepts
  - Number of rooms
  - Configuration status

---

### 6. **Floor Table Page** (`/floors/:floorId`)
**Purpose**: Configure associations between concepts and room objects

**Features**:
- View concepts from selected PDF
- View available room objects
- Create associations between concepts and objects
- AI generates Turkish associations (4-6 sentences)
- Save associations to database
- Visual confirmation of configured associations

**What You Do**:
1. Select a room from dropdown
2. Click "Configure Associations"
3. AI generates vivid Turkish associations for each concept-object pair
4. Review associations in table format
5. Associations automatically saved

**Association Generation**:
- Uses Llama 3.3 70B model
- Creates 4-6 sentence associations in Turkish
- Engaging, visual, memorable content
- Each association connects concept meaning to object characteristics

**UI Elements**:
- Room selector dropdown
- "Configure Associations" button
- Data table with columns:
  - Object Image
  - Object Name (Turkish)
  - Concept Name
  - Association (4-6 sentences in Turkish)
- Loading states during generation

---

### 7. **Walkthrough Page** (`/walkthrough`)
**Purpose**: Experience your memory palace journey

**Features**:
- Select floor and room to start walkthrough
- Visual journey through associations
- See object images with their concepts
- Read associations in sequence
- Story-based mode with smooth transitions
- Navigate forward/backward through objects

**What You Do**:
1. Select floor from dropdown
2. Select room from dropdown
3. Click "Start Walkthrough"
4. View each object-concept pair in sequence
5. Read the Turkish association
6. Click "Next" to continue journey

**Story Mode**:
- Each association flows naturally to the next
- Transitions guide you spatially through the room
- Creates coherent narrative for better memory

**UI Elements**:
- Floor and room selectors
- Large object image display
- Concept name prominently shown
- Turkish association text (4-6 sentences)
- Previous/Next navigation buttons
- Progress indicator

---

### 8. **History Page** (`/history`)
**Purpose**: Review past learning and track progress

**Features**:
- View all created memory palaces
- See which concepts you've memorized
- Track completion status by floor
- Review past associations
- Filter by date, floor, or room

**What You See**:
- Timeline of learning activities
- List of floors with completion percentage
- Recently reviewed associations
- Statistics dashboard

---

## 🔧 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  - TypeScript + Vite                                     │
│  - TanStack Query for data fetching                      │
│  - shadcn/ui components                                  │
│  - Tailwind CSS styling                                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ HTTP Requests
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│  - RESTful API endpoints                                 │
│  - PDF text extraction                                   │
│  - Vector database integration                           │
│  - AI model orchestration                                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌──────────┐
│  Supabase │  │   Groq    │  │  fal.ai  │
│ Database  │  │    AI     │  │  Vision  │
│           │  │  (Llama)  │  │  Models  │
└───────────┘  └───────────┘  └──────────┘
```

### Data Flow

#### 1. PDF Processing Flow
```
User uploads PDF 
    → Backend extracts text (PyPDF2/Groq)
    → Stores in Supabase
    → AI analyzes text
    → Generates concepts with descriptions
    → Stores concepts in vector database
```

#### 2. Room Creation Flow
```
User uploads room photo
    → Enable auto-detect
    → AI (Llama 4 Vision) analyzes room
    → Detects objects (Turkish names)
    → AI (Qwen Image Edit) extracts each object
    → Stores object images in Supabase Storage
    → Creates room record in database
```

#### 3. Association Generation Flow
```
User selects floor + room + concepts
    → Backend fetches concepts from vector DB
    → Backend fetches room objects
    → AI (Llama 3.3 70B) generates associations
    → Creates vivid 4-6 sentence associations in Turkish
    → Stores associations in database
    → Returns to frontend for display
```

#### 4. Walkthrough Flow
```
User selects floor + room
    → Backend fetches associations (filtered by floor_id + room_id)
    → Frontend displays in sequence
    → Shows object image + concept + association
    → User navigates through memory palace
```

### AI Models Used

#### 1. **Groq Llama 3.3 70B** (`llama-3.3-70b-versatile`)
- **Purpose**: Association generation, concept extraction
- **Temperature**: 0.8 (creative associations)
- **Output**: Turkish text, 4-6 sentences
- **Features**: Fast inference, high quality Turkish output

#### 2. **Llama 4 Scout Vision** (`llama-4-scout-17b-16e-instruct`)
- **Purpose**: Room object detection, image analysis
- **Input**: Room photos
- **Output**: Object names and descriptions (Turkish)

#### 3. **Qwen Image Edit** (`fal-ai/qwen-image-edit/image-to-image`)
- **Purpose**: Object extraction from room photos
- **Input**: Room image + text prompt
- **Output**: Isolated object images
- **Parameters**: 
  - Guidance scale: 5.0
  - Strength: 0.9
  - Inference steps: 28

### Database Schema

#### **pdfs** table
```sql
- id (uuid, primary key)
- user_id (uuid, references auth.users)
- title (text)
- file_path (text)
- upload_date (timestamp)
- extracted_text (text)
```

#### **concepts** table
```sql
- id (uuid, primary key)
- pdf_id (uuid, references pdfs)
- concept (text) -- Turkish
- description (text) -- Turkish
- created_at (timestamp)
```

#### **rooms** table
```sql
- id (uuid, primary key)
- user_id (uuid)
- name (text) -- Turkish room name
- room_image_url (text)
- created_at (timestamp)
```

#### **room_objects** table
```sql
- id (uuid, primary key)
- room_id (uuid, references rooms)
- object_name (text) -- Turkish name
- short_description (text) -- Turkish description
- image_url (text)
- position (integer)
```

#### **floors** table
```sql
- id (uuid, primary key)
- user_id (uuid)
- name (text) -- Floor/topic name
- pdf_id (uuid, references pdfs)
- created_at (timestamp)
```

#### **associations** table
```sql
- id (uuid, primary key)
- floor_id (uuid, references floors)
- room_id (uuid, references rooms)
- concept_id (uuid, references concepts)
- object_id (uuid, references room_objects)
- association_text (text) -- Turkish, 4-6 sentences
- created_at (timestamp)
```

---

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Query (React Query)** - Data fetching and caching
- **TanStack Table** - Powerful data tables
- **shadcn/ui** - Beautiful, accessible components
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **React Router** - Client-side routing
- **Sonner** - Toast notifications

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.10+** - Programming language
- **Uvicorn** - ASGI server
- **Groq API** - AI model access (Llama)
- **fal.ai API** - Image processing models
- **Supabase Client** - Database and storage
- **ChromaDB** - Vector database for concepts
- **python-dotenv** - Environment management

### Database & Storage
- **Supabase PostgreSQL** - Main database
- **Supabase Storage** - Image and file storage
- **ChromaDB** - Vector embeddings for concept search

### AI & ML
- **Groq Llama 3.3 70B** - Association generation
- **Llama 4 Scout Vision** - Image analysis
- **Qwen Image Edit** - Object extraction
- **Sentence Transformers** - Text embeddings

---

## 🚀 Installation & Setup

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.10+
- **Supabase Account** (free tier works)
- **Groq API Key** (free tier available)
- **fal.ai API Key** (free tier available)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/mind-palace-craft.git
cd mind-palace-craft
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
# VITE_SUPABASE_URL=your_supabase_url
# VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd alpaca

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with API keys
# GROQ_API_KEY=your_groq_api_key
# FAL_API_KEY=your_fal_api_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_service_key
```

### 4. Database Setup

1. Create Supabase project at https://supabase.com
2. Run SQL migrations in Supabase SQL Editor:
   - Create tables: `pdfs`, `concepts`, `rooms`, `room_objects`, `floors`, `associations`
   - Set up storage buckets: `pdfs`, `room-images`, `object-images`
   - Configure Row Level Security (RLS) policies

3. Sample SQL for tables:

```sql
-- PDFs table
CREATE TABLE pdfs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  file_path TEXT NOT NULL,
  upload_date TIMESTAMP DEFAULT NOW(),
  extracted_text TEXT
);

-- Concepts table
CREATE TABLE concepts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  pdf_id UUID REFERENCES pdfs(id) ON DELETE CASCADE,
  concept TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Rooms table
CREATE TABLE rooms (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  room_image_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Room Objects table
CREATE TABLE room_objects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
  object_name TEXT NOT NULL,
  short_description TEXT,
  image_url TEXT NOT NULL,
  position INTEGER DEFAULT 0
);

-- Floors table
CREATE TABLE floors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  pdf_id UUID REFERENCES pdfs(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Associations table
CREATE TABLE associations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  floor_id UUID REFERENCES floors(id) ON DELETE CASCADE,
  room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
  concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
  object_id UUID REFERENCES room_objects(id) ON DELETE CASCADE,
  association_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Static Assets Setup

Place the 10 object images in the static folder:

```bash
mkdir -p app/static/img
# Copy these 10 images to app/static/img/:
# - Black pen.jpg
# - Computer monitor.jpg
# - Computer mouse.jpg
# - Desk lamp.jpg
# - Green water bottle.jpg
# - Keyboard.jpg
# - Notebook (with yellow ribbon).jpg
# - Potted plant.jpg
# - Quote frame.jpg
# - Soldier figurine.jpg
```

### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd alpaca
python api_server.py
# Server runs on http://localhost:8081
```

**Terminal 2 - Frontend:**
```bash
npm run dev
# App runs on http://localhost:5173
```

---

## 🎯 Usage Guide

### Step-by-Step Tutorial

#### Step 1: Upload Study Material
1. Go to **PDFs** page
2. Click **"Add PDF"**
3. Upload your textbook/notes PDF
4. Wait for processing
5. Click **"Generate Concepts"**
6. AI extracts key concepts in Turkish

#### Step 2: Create Memory Palace Room
1. Go to **Rooms** page
2. Click **"New Room"**
3. Enter room name (e.g., "Çalışma Odam")
4. Upload room photo
5. Enable **"Auto-detect objects"**
6. Set number of objects (5-10 recommended)
7. Click **"Detect Objects"**
8. Wait for AI to detect and extract objects
9. Review Turkish object names
10. Click **"Save"**

#### Step 3: Create Floor (Topic)
1. Go to **Floors** page
2. Click **"New Floor"**
3. Enter floor name (e.g., "Fizik - Bölüm 1")
4. Select PDF from dropdown
5. Click **"Create Floor"**

#### Step 4: Configure Associations
1. Go to **Floors** page
2. Click on your floor card
3. Select room from dropdown
4. Click **"Configure Associations"**
5. AI generates Turkish associations (4-6 sentences each)
6. Review associations in table
7. Associations auto-saved

#### Step 5: Start Learning
1. Go to **Walkthrough** page
2. Select floor and room
3. Click **"Start Walkthrough"**
4. Read each association carefully
5. Visualize the scene in your mind
6. Click **"Next"** to continue
7. Repeat walkthrough multiple times

#### Step 6: Review and Reinforce
1. Go back to walkthrough regularly
2. Try to recall associations before revealing
3. Use **History** page to track progress
4. Reconfigure associations if needed

---

## 📁 Project Structure

```
mind-palace-craft/
├── src/                          # Frontend source code
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── NewRoomModal.tsx      # Room creation modal
│   │   └── ...
│   ├── pages/                    # Page components
│   │   ├── Index.tsx             # Home page
│   │   ├── PDFs.tsx              # PDFs management
│   │   ├── Concepts.tsx          # Concepts view
│   │   ├── Rooms.tsx             # Rooms management
│   │   ├── Floors.tsx            # Floors management
│   │   ├── FloorTable.tsx        # Association configuration
│   │   ├── Walkthrough.tsx       # Memory palace walkthrough
│   │   └── History.tsx           # Learning history
│   ├── integrations/             # API integrations
│   │   └── supabase/             # Supabase client
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utility functions
│   └── App.tsx                   # Main app component
│
├── alpaca/                       # Backend source code
│   ├── api_server.py             # FastAPI server
│   ├── association_generator.py # AI association generation
│   ├── concept_generator.py     # Concept extraction
│   ├── fal_service.py            # fal.ai integration
│   ├── vector_db.py              # ChromaDB management
│   ├── rag_service.py            # RAG for concepts
│   ├── pdf_extract.py            # PDF text extraction
│   └── requirements.txt          # Python dependencies
│
├── app/                          # Static assets
│   └── static/
│       └── img/                  # Object images
│
├── docs/                         # Documentation
│   ├── AUTO_DETECT_OBJECTS.md
│   ├── CHANGES_SUMMARY.md
│   ├── TURKISH_LANGUAGE_UPDATE.md
│   └── TURKISH_EXPLICIT_PROMPTS.md
│
├── public/                       # Public assets
├── index.html                    # HTML entry point
├── package.json                  # Node dependencies
├── tsconfig.json                 # TypeScript config
├── vite.config.ts                # Vite configuration
├── tailwind.config.ts            # Tailwind CSS config
└── README.md                     # This file
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8081
```

### Endpoints

#### Health Check
```http
GET /health
```
Returns API status

#### PDF Management
```http
POST /add_pdf
Content-Type: application/json
Body: { "pdf_text": "...", "title": "..." }
```

#### Concept Generation
```http
POST /generate_concepts
Content-Type: application/json
Body: { "pdf_text": "..." }
```

#### Association Generation
```http
POST /generate_associations
Content-Type: application/json
Body: {
  "concepts": [...],
  "room_objects": [...],
  "pdf_text": "..."
}
```

#### Room Object Analysis
```http
POST /analyze_room_image
Content-Type: multipart/form-data
Body: file (image)
```

#### Object Detection (Auto-detect)
```http
POST /detect_room_objects
Content-Type: multipart/form-data
Body: file (image), num_objects (integer)
```

#### Object Extraction
```http
POST /extract_object_image
Content-Type: multipart/form-data
Body: room_image (file), object_name (string), object_description (string)
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation when needed
- Test your changes thoroughly

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Memory Palace Technique** - Ancient mnemonic method
- **Groq** - Fast AI inference
- **fal.ai** - Image processing models
- **Supabase** - Backend infrastructure
- **shadcn/ui** - Beautiful components
- **The Open Source Community** - For amazing tools and libraries

---

## 📧 Contact & Support

- **Issues**: Report bugs via GitHub Issues
- **Questions**: Open a discussion on GitHub
- **Documentation**: See `/docs` folder for detailed guides

---

## 🎓 Educational Use

Mind Palace Craft is designed for educational purposes. Perfect for:
- Students preparing for exams
- Professionals learning new skills
- Language learners memorizing vocabulary
- Anyone wanting to improve memory

---

## 🌟 Future Roadmap

- [ ] Mobile app (iOS & Android)
- [ ] Collaborative memory palaces
- [ ] Spaced repetition integration
- [ ] Audio narration for associations
- [ ] Multi-language support (beyond Turkish)
- [ ] Gamification and achievements
- [ ] Export to PDF/Anki
- [ ] 3D room visualization
- [ ] AR walkthrough with phone camera

---

## 💖 Support the Project

If you find Mind Palace Craft helpful:
- ⭐ Star this repository
- 🐦 Share on social media
- 📝 Write a blog post about your experience
- 💡 Suggest new features
- 🐛 Report bugs

---

**Made with ❤️ and AI**

*Transform your learning, one memory at a time.*
