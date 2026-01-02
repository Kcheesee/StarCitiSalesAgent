# 🚀 StarCiti Sales Agent

> AI-powered voice consultant for Star Citizen ships with intelligent recommendations, automated PDF reports, and email delivery.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://starciti-backend.onrender.com)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📖 Overview

**StarCiti Sales Agent** is a full-stack AI application that helps Star Citizen players discover and select the perfect ships for their playstyle through natural voice conversations. The system uses advanced AI to understand player preferences, analyze a database of 150+ ships, and deliver professional fleet recommendations via beautifully designed PDFs sent directly to their email.

### 🎯 Key Features

- **🎤 Voice-First Interface**: Natural conversation flow using OpenAI Whisper (speech-to-text) and ElevenLabs (text-to-speech)
- **🤖 AI-Powered Recommendations**: Claude 3.7 Sonnet analyzes player requirements and recommends optimal ships
- **🔍 Semantic Ship Search**: RAG (Retrieval-Augmented Generation) system with vector embeddings for intelligent ship matching
- **📄 Automated PDF Generation**: Professional fleet composition guides with ship specs, images, and upgrade paths
- **📧 Email Delivery**: SendGrid integration for instant PDF delivery to players
- **🎨 Premium Design**: Dark-themed PDFs matching Star Citizen's aesthetic
- **⚡ Real-time Webhooks**: ElevenLabs post-call webhooks for automated transcript processing
- **🗄️ PostgreSQL + pgvector**: Robust database with vector similarity search

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Relational database with pgvector extension
- **SQLAlchemy** - ORM for database operations
- **OpenAI API** - Whisper for speech-to-text, embeddings for RAG
- **Anthropic Claude API** - Conversational AI and ship analysis
- **ElevenLabs API** - High-quality text-to-speech synthesis
- **SendGrid API** - Transactional email delivery
- **WeasyPrint** - HTML/CSS to PDF rendering
- **Jinja2** - PDF template engine

### Frontend
- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

### Infrastructure
- **Render** - Cloud hosting (backend + database)
- **Vercel** - Frontend hosting
- **GitHub Actions** - CI/CD pipeline

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Interface                          │
│                    (React + Voice Recording)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Conversation │  │   Voice      │  │   Ship Search      │   │
│  │   Manager    │  │   Service    │  │   (RAG + Vector)   │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │  Anthropic   │  │ ElevenLabs   │
│   (Whisper)  │  │   (Claude)   │  │    (TTS)     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
        ┌────────────────────────────────────────┐
        │  ElevenLabs Webhook (Post-Call)        │
        │  → Transcript Processing                │
        │  → Ship Analysis (Claude)               │
        │  → PDF Generation (WeasyPrint)          │
        │  → Email Delivery (SendGrid)            │
        └────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │    PostgreSQL + pgvector                │
        │  • Ships (150+ with specs)              │
        │  • Conversations & Transcripts          │
        │  • Vector Embeddings (1536-dim)         │
        └────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **API Keys**:
  - OpenAI API key ([Get it here](https://platform.openai.com/api-keys))
  - Anthropic API key ([Get it here](https://console.anthropic.com/))
  - ElevenLabs API key ([Get it here](https://elevenlabs.io/))
  - SendGrid API key ([Get it here](https://sendgrid.com/))

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Kcheesee/StarCitiSalesAgent.git
cd StarCitiSalesAgent
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
createdb starciti_sales

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and database URL
```

**`.env` Configuration:**
```env
DATABASE_URL=postgresql://localhost/starciti_sales
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=your_voice_id
SENDGRID_API_KEY=SG...
SENDGRID_FROM_EMAIL=your@email.com
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

#### 3. Database Setup & Data Population

```bash
# Run database migrations
alembic upgrade head

# Fetch ship data from Star Citizen Wiki API
python scripts/fetch_ships.py

# Transform and load into database
python scripts/etl_pipeline.py

# Generate vector embeddings for semantic search
python scripts/generate_embeddings.py
```

#### 4. Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

#### 5. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 📡 API Documentation

### Core Endpoints

#### Start Conversation
```http
POST /api/conversations/start
Content-Type: application/json

{
  "user_name": "Pilot",
  "user_email": "pilot@example.com"
}

Response:
{
  "conversation_id": 1,
  "user_name": "Pilot",
  "status": "active",
  "started_at": "2026-01-02T10:30:00Z"
}
```

#### Send Message
```http
POST /api/conversations/{id}/message
Content-Type: application/json

{
  "message": "I'm looking for a combat ship under $200"
}

Response:
{
  "response": "Great! For combat under $200, I'd recommend...",
  "recommended_ships": [
    {
      "name": "Aegis Avenger Titan",
      "manufacturer": "Aegis Dynamics",
      "price_usd": 50,
      "focus": "Multi-role",
      "recommendation_reason": "Excellent starter combat ship"
    }
  ]
}
```

#### Voice Transcription
```http
POST /api/voice/transcribe
Content-Type: multipart/form-data

audio_file: <audio.mp3>

Response:
{
  "transcript": "I'm looking for a combat ship",
  "confidence": 0.98
}
```

#### Complete Conversation & Generate PDFs
```http
POST /api/conversations/{id}/complete

Response:
{
  "status": "completed",
  "transcript_pdf_url": "/outputs/transcripts/conv_1_transcript.pdf",
  "fleet_guide_pdf_url": "/outputs/fleet_guides/conv_1_fleet_guide.pdf",
  "email_sent": true
}
```

### Webhook Endpoints

#### ElevenLabs Post-Call Webhook
```http
POST /api/webhooks/elevenlabs/post-call
Content-Type: application/json
elevenlabs-signature: <hmac-sha256-signature>

{
  "type": "post_call_transcription",
  "data": {
    "conversation_id": "conv_xxx",
    "transcript": [
      {"role": "user", "message": "...", "time": 1234567890},
      {"role": "assistant", "message": "...", "time": 1234567891}
    ],
    "analysis": {...}
  }
}
```

**Full API Documentation:** Visit `/docs` when running the server

---

## 🎨 PDF Templates

The system generates two professional PDFs:

### 1. Conversation Transcript
- Full conversation history
- User preferences summary
- Timestamp and session details
- Star Citizen branded design

### 2. Fleet Composition Guide
- **Page 1**: Top recommended ships with images, specs, and pricing
- **Page 2**: Fleet analysis and upgrade paths
- **Page 3**: Purchase links and next steps

**Templates located in:** `backend/templates/`

---

## 🔧 Key Technical Decisions

### Why WeasyPrint over Playwright?

**Problem:** Playwright requires Chromium browser + system dependencies that need root access, incompatible with Render free tier.

**Solution:** WeasyPrint renders HTML/CSS to PDF without browser automation:
- ✅ Pure Python (no system dependencies)
- ✅ Works on containerized/limited environments
- ✅ Maintains premium template design
- ✅ More reliable for server-side PDF generation

### RAG System Implementation

1. **Embedding Generation**: Each ship's specs, description, and metadata are combined into searchable text
2. **Vector Storage**: OpenAI embeddings (1536-dim) stored in PostgreSQL with pgvector
3. **Query Processing**: User messages are embedded and compared via cosine similarity
4. **Context Injection**: Top-k ships are injected into Claude's context for recommendations

### Database Session Management

Added `db.refresh(conversation)` before PDF generation to prevent SQLAlchemy session caching issues where webhook updates weren't immediately visible to background tasks.

---

## 📊 Project Structure

```
StarCitiSalesAgent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Environment configuration
│   │   ├── database.py                # SQLAlchemy setup
│   │   ├── models/                    # Database models
│   │   │   ├── ship.py                # Ship, Manufacturer, Embeddings
│   │   │   └── conversation.py        # Conversation tracking
│   │   ├── api/                       # API routes
│   │   │   ├── conversations.py       # Conversation endpoints
│   │   │   ├── voice.py               # Voice processing
│   │   │   ├── ships.py               # Ship search
│   │   │   └── webhooks.py            # ElevenLabs webhooks
│   │   ├── services/                  # Business logic
│   │   │   ├── ai_consultant.py       # Claude conversation manager
│   │   │   ├── rag_system.py          # Vector search
│   │   │   ├── voice_service.py       # Whisper + ElevenLabs
│   │   │   ├── ship_analyzer.py       # Extract ship mentions
│   │   │   ├── pdf_generator_weasyprint.py  # PDF creation
│   │   │   └── email_service.py       # SendGrid integration
│   │   └── utils/
│   │       └── prompts.py             # AI system prompts
│   ├── scripts/
│   │   ├── fetch_ships.py             # Data collection
│   │   ├── etl_pipeline.py            # Transform & load
│   │   └── generate_embeddings.py     # Vector creation
│   ├── templates/                     # Jinja2 PDF templates
│   │   ├── transcript_template.html
│   │   └── fleet_guide_template.html
│   ├── requirements.txt
│   ├── render.yaml                    # Render deployment config
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── VoiceInterface.jsx     # Voice recording UI
│   │   │   ├── ChatInterface.jsx      # Text chat
│   │   │   ├── ShipCard.jsx           # Ship display
│   │   │   └── EmailCapture.jsx       # Email input
│   │   ├── hooks/
│   │   │   ├── useConversation.js     # Conversation state
│   │   │   └── useVoiceRecording.js   # Audio capture
│   │   └── services/
│   │       └── api.js                 # API client
│   ├── package.json
│   └── vite.config.js
│
├── data/                              # Generated during setup
│   ├── raw_ships/                     # Raw API responses
│   └── ship_images/                   # Ship images
│
├── outputs/                           # Generated PDFs
│   ├── transcripts/
│   └── fleet_guides/
│
└── README.md
```

---

## 🚢 Deployment

### Backend (Render)

1. **Connect GitHub Repository** to Render
2. **Create Web Service**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Create PostgreSQL Database** (same project)
4. **Set Environment Variables**:
   - All API keys
   - `DATABASE_URL` (auto-linked)
   - `ENVIRONMENT=production`
5. **Run Database Migrations** in Render Shell:
   ```bash
   alembic upgrade head
   python scripts/etl_pipeline.py
   python scripts/generate_embeddings.py
   ```

### Frontend (Vercel)

1. **Connect GitHub Repository** to Vercel
2. **Configure Build Settings**:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. **Set Environment Variables**:
   - `VITE_API_URL=https://your-backend.onrender.com`

### Webhook Configuration

1. **ElevenLabs Dashboard** → Webhooks
2. **Add Webhook URL**: `https://your-backend.onrender.com/api/webhooks/elevenlabs/post-call`
3. **Copy Webhook Secret** → Add to Render environment variables
4. **Enable Post-Call Transcription** webhook

---

## 📈 Performance & Costs

### API Costs (Per Conversation)

- **OpenAI Whisper**: ~$0.18/30min of audio
- **OpenAI Embeddings**: ~$0.001 (one-time for 150 ships)
- **Anthropic Claude**: ~$0.50-2.00 (depends on conversation length)
- **ElevenLabs TTS**: ~$0.30-1.00 (character-based)
- **Total per conversation**: ~$1-3

### Monthly Infrastructure

- **PostgreSQL (Render)**: $7/month
- **Backend Hosting (Render)**: Free tier or $7/month
- **Frontend (Vercel)**: Free
- **SendGrid**: Free (100 emails/day)
- **Total**: ~$7-14/month

---

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/

# Test specific endpoint
pytest tests/test_conversations.py -v
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Star Citizen Wiki API** for ship data
- **Cloud Imperium Games** for Star Citizen
- **OpenAI** for Whisper and embeddings
- **Anthropic** for Claude AI
- **ElevenLabs** for voice synthesis

---

## 📧 Contact

**Your Name** - [@yourusername](https://twitter.com/yourusername)

**Project Link**: [https://github.com/Kcheesee/StarCitiSalesAgent](https://github.com/Kcheesee/StarCitiSalesAgent)

**Live Demo**: [https://starciti-backend.onrender.com](https://starciti-backend.onrender.com)

---

<p align="center">Made with ❤️ for the Star Citizen community</p>
