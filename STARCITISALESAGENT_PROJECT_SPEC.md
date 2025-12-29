# StarCitiSalesAgent - Complete Project Specification

## Project Overview

**Name:** StarCitiSalesAgent  
**Type:** Voice-Powered AI Sales Consultant  
**Purpose:** Help Star Citizen players discover and select ships based on their playstyle, budget, and fleet goals through natural voice conversation, then deliver professional fleet recommendations via email.

**Key Differentiator:** This isn't just a chatbot - it's a full sales experience with voice interaction and professional deliverables, demonstrating enterprise-level AI implementation.

---

## Technical Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL (ship data + conversation storage)
- OpenAI Whisper API (speech-to-text)
- ElevenLabs API (text-to-speech)
- Claude API (conversational AI + RAG)
- ReportLab or WeasyPrint (PDF generation)
- SendGrid (email delivery)
- ChromaDB or Pinecone (vector embeddings for ship descriptions)

**Frontend:**
- React 18+
- WebSocket (real-time voice streaming)
- Web Audio API (audio recording/playback)
- Tailwind CSS (styling)

**Deployment:**
- Backend: Render or Railway
- Frontend: Vercel or Netlify
- Database: Render PostgreSQL or Supabase
- Static Assets: Cloudflare R2 or S3 (for ship images)

---

## Database Schema

### Ships Table
```sql
CREATE TABLE ships (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    class_name VARCHAR(255),
    manufacturer VARCHAR(255),
    focus VARCHAR(255), -- e.g., "Exploration", "Combat", "Cargo"
    type VARCHAR(100), -- e.g., "Ship", "Vehicle", "Snub"
    
    -- Pricing
    price_usd DECIMAL(10,2),
    price_auec INTEGER,
    
    -- Capacity
    cargo_capacity INTEGER, -- SCU
    min_crew INTEGER,
    max_crew INTEGER,
    
    -- Dimensions
    length DECIMAL(10,2), -- meters
    beam DECIMAL(10,2),
    height DECIMAL(10,2),
    mass INTEGER, -- kg
    
    -- Performance (if available)
    max_speed INTEGER,
    scm_speed INTEGER,
    
    -- Metadata
    description TEXT,
    marketing_description TEXT, -- From RSI website
    image_url VARCHAR(500),
    store_url VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ships_manufacturer ON ships(manufacturer);
CREATE INDEX idx_ships_focus ON ships(focus);
CREATE INDEX idx_ships_price_usd ON ships(price_usd);
```

### Ship Hardpoints Table
```sql
CREATE TABLE ship_hardpoints (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,
    
    hardpoint_name VARCHAR(255),
    size INTEGER, -- Weapon/component size (S1, S2, etc.)
    type VARCHAR(100), -- "Weapon", "Turret", "Missile", "Utility"
    category VARCHAR(100), -- "Fixed", "Gimbaled", "Manned Turret"
    quantity INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hardpoints_ship ON ship_hardpoints(ship_id);
```

### Ship Components Table
```sql
CREATE TABLE ship_components (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,
    
    component_type VARCHAR(100), -- "Shield", "Power Plant", "Cooler", "Quantum Drive"
    component_name VARCHAR(255),
    size INTEGER,
    manufacturer VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Ship Vehicle Bays Table
```sql
CREATE TABLE ship_vehicle_bays (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,
    
    bay_type VARCHAR(100), -- "Vehicle", "Snub Fighter", "Docking Collar"
    capacity INTEGER, -- How many vehicles
    max_size VARCHAR(50), -- "Small", "Medium", "Large" or specific vehicle names
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Ship Descriptions (for RAG/Embeddings)
```sql
CREATE TABLE ship_embeddings (
    id SERIAL PRIMARY KEY,
    ship_id INTEGER REFERENCES ships(id) ON DELETE CASCADE,
    
    description_text TEXT NOT NULL,
    embedding VECTOR(1536), -- For OpenAI embeddings
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_ship ON ship_embeddings(ship_id);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_uuid VARCHAR(255) UNIQUE NOT NULL,
    
    user_email VARCHAR(255),
    user_budget_usd INTEGER,
    user_playstyle VARCHAR(100), -- "Solo", "Crew", "Mixed"
    user_preferences JSONB, -- Store flexible user input
    
    -- Conversation state
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'abandoned'
    transcript JSONB, -- Array of {role: "user"|"assistant", content: "..."}
    
    -- Recommendations
    recommended_ships JSONB, -- Array of ship IDs + reasoning
    
    -- Documents
    transcript_pdf_path VARCHAR(500),
    fleet_guide_pdf_path VARCHAR(500),
    email_sent BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_email ON conversations(user_email);
```

---

## API Endpoints Specification

### Phase 1: Text-Based Consultant

#### POST /api/conversations/start
**Description:** Initialize a new conversation session  
**Request Body:**
```json
{
  "user_email": "optional@email.com"
}
```
**Response:**
```json
{
  "conversation_id": "uuid-here",
  "message": "Welcome message from AI"
}
```

#### POST /api/conversations/{conversation_id}/message
**Description:** Send a user message and get AI response  
**Request Body:**
```json
{
  "message": "I want a cargo ship for solo play under $200"
}
```
**Response:**
```json
{
  "conversation_id": "uuid-here",
  "user_message": "I want a cargo ship...",
  "ai_response": "Based on your budget...",
  "recommended_ships": [
    {
      "id": 123,
      "name": "MISC Freelancer",
      "reason": "Excellent solo cargo ship with good defenses"
    }
  ]
}
```

#### GET /api/conversations/{conversation_id}
**Description:** Get conversation history  
**Response:**
```json
{
  "conversation_id": "uuid-here",
  "transcript": [
    {"role": "assistant", "content": "Welcome! ..."},
    {"role": "user", "content": "I want a cargo ship..."},
    {"role": "assistant", "content": "Based on your budget..."}
  ],
  "recommended_ships": [...],
  "status": "active"
}
```

#### POST /api/conversations/{conversation_id}/complete
**Description:** Mark conversation as complete, trigger PDF generation  
**Response:**
```json
{
  "conversation_id": "uuid-here",
  "status": "completed",
  "transcript_pdf": "/pdfs/transcript_uuid.pdf",
  "fleet_guide_pdf": "/pdfs/fleet_uuid.pdf"
}
```

### Phase 2: Voice Integration

#### POST /api/voice/transcribe
**Description:** Convert audio to text  
**Request:** multipart/form-data with audio file  
**Response:**
```json
{
  "transcription": "I want a cargo ship for solo play"
}
```

#### POST /api/voice/synthesize
**Description:** Convert text to speech  
**Request Body:**
```json
{
  "text": "Based on your budget, I recommend the MISC Freelancer"
}
```
**Response:** Audio file (binary stream)

#### WebSocket /ws/voice/{conversation_id}
**Description:** Real-time bidirectional voice streaming  
**Messages:**
- Client → Server: Audio chunks
- Server → Client: Transcription + AI response audio

### Phase 3: Document Generation

#### GET /api/pdfs/transcript/{conversation_id}
**Description:** Download transcript PDF  
**Response:** PDF file

#### GET /api/pdfs/fleet-guide/{conversation_id}
**Description:** Download fleet composition guide PDF  
**Response:** PDF file

### Phase 4: Email Delivery

#### POST /api/email/send-recommendations
**Description:** Email both PDFs to user  
**Request Body:**
```json
{
  "conversation_id": "uuid-here",
  "user_email": "user@example.com"
}
```
**Response:**
```json
{
  "status": "sent",
  "email": "user@example.com",
  "sent_at": "2025-12-23T10:00:00Z"
}
```

---

## PHASE 1: Data Foundation & Text-Based AI

### Objective
Build comprehensive ship database and working text-based consultant that can recommend ships based on user input.

### Tasks

#### 1.1: API Exploration & Data Discovery
**Duration:** 1 day  
**Tasks:**
- [ ] Open `https://api.star-citizen.wiki/api/v2/vehicles/` in browser
- [ ] Test endpoints for specific ships (300i, Carrack, Prospector, etc.)
- [ ] Document all available fields per ship
- [ ] Identify data gaps (weapon sizes, vehicle bays, descriptions)
- [ ] Test if API has pagination or provides full ship list

**Acceptance Criteria:**
- ✅ Documented list of all available API fields
- ✅ Identified which fields are consistently available
- ✅ Clear list of missing data we need to scrape elsewhere

**Deliverable:** `DATA_MAPPING.md` document showing API structure

---

#### 1.2: Comprehensive Ship Data Collection
**Duration:** 3-4 days  
**Tasks:**
- [ ] Write Python script to fetch ALL ships from API (150+ ships)
- [ ] Store raw JSON responses for inspection
- [ ] Scrape RSI ship pages for marketing descriptions
  - Target: `https://robertsspaceindustries.com/pledge/ships`
  - Extract: Ship descriptions, images, store links
- [ ] (Optional) Scrape erkul.games for detailed loadout data if API insufficient
- [ ] Handle rate limiting and errors gracefully
- [ ] Validate data completeness (flag ships with missing critical fields)

**Acceptance Criteria:**
- ✅ Script successfully fetches 150+ ships from wiki API
- ✅ Marketing descriptions scraped from RSI for all ships
- ✅ Ship images downloaded and stored
- ✅ Data validation report showing completeness %

**Deliverables:**
- `fetch_ships.py` - Data collection script
- `/data/raw_ships/` - Raw JSON files
- `/data/ship_images/` - Downloaded images
- `data_completeness_report.txt`

---

#### 1.3: Database Setup & ETL
**Duration:** 2 days  
**Tasks:**
- [ ] Set up PostgreSQL locally
- [ ] Create all tables (ships, hardpoints, components, vehicle_bays, embeddings, conversations)
- [ ] Write ETL script to transform raw JSON → structured database
- [ ] Insert all ships with complete data
- [ ] Create database indexes for performance
- [ ] Add seed data for testing

**Acceptance Criteria:**
- ✅ All tables created with proper relationships
- ✅ 150+ ships inserted successfully
- ✅ Hardpoints, components populated where available
- ✅ Query performance tested (< 100ms for typical queries)

**Deliverables:**
- `schema.sql` - Database schema
- `etl_pipeline.py` - ETL script
- `seed_test_data.sql` - Test data for development

---

#### 1.4: RAG System Setup
**Duration:** 2 days  
**Tasks:**
- [ ] Generate embeddings for ship descriptions using OpenAI
- [ ] Store embeddings in `ship_embeddings` table
- [ ] Implement semantic search function
- [ ] Test: Query "fast combat ship" returns relevant results
- [ ] Optimize retrieval (top-k results, similarity threshold)

**Acceptance Criteria:**
- ✅ All ship descriptions embedded and stored
- ✅ Semantic search returns relevant ships for test queries
- ✅ Search results ranked by relevance

**Deliverable:** `rag_system.py` - RAG implementation

---

#### 1.5: AI Consultant System Prompt
**Duration:** 1 day  
**Tasks:**
- [ ] Write comprehensive system prompt for Claude:
  - Persona: Professional ship sales consultant
  - Tone: Friendly, knowledgeable, not pushy
  - Discovery questions: Budget, playstyle, crew size, preferred roles
  - Recommendation format: Ship name, reasoning, alternatives
- [ ] Test prompt with various user scenarios
- [ ] Refine based on output quality

**Acceptance Criteria:**
- ✅ System prompt produces helpful, accurate recommendations
- ✅ AI asks clarifying questions when needed
- ✅ Recommendations include reasoning

**Deliverable:** `system_prompt.txt`

---

#### 1.6: Conversational AI Logic
**Duration:** 3 days  
**Tasks:**
- [ ] Build conversation manager:
  - Track conversation state
  - Manage multi-turn context
  - Integrate RAG for ship retrieval
- [ ] Implement Claude API integration
- [ ] Add conversation flow logic:
  - Greeting → Discovery → Recommendations → Follow-up
- [ ] Store conversations in database
- [ ] Test multi-turn conversations

**Acceptance Criteria:**
- ✅ AI maintains context across multiple messages
- ✅ Retrieves relevant ships from database via RAG
- ✅ Provides coherent, helpful recommendations
- ✅ Conversations saved to database

**Deliverable:** `ai_consultant.py` - Core AI logic

---

#### 1.7: FastAPI Backend
**Duration:** 2 days  
**Tasks:**
- [ ] Set up FastAPI project structure
- [ ] Implement all Phase 1 endpoints:
  - POST /api/conversations/start
  - POST /api/conversations/{id}/message
  - GET /api/conversations/{id}
- [ ] Add CORS middleware
- [ ] Add error handling and logging
- [ ] Write API tests

**Acceptance Criteria:**
- ✅ All endpoints working and tested
- ✅ Proper error responses (400, 404, 500)
- ✅ Request/response validation

**Deliverable:** `/backend` - Complete FastAPI app

---

#### 1.8: React Frontend (Text Chat)
**Duration:** 3 days  
**Tasks:**
- [ ] Create React app with Vite
- [ ] Build chat interface:
  - Message list (user vs AI styling)
  - Input box
  - Send button
  - "AI is thinking..." indicator
- [ ] Connect to FastAPI backend
- [ ] Display ship recommendations with images
- [ ] Add conversation history display
- [ ] Style with Tailwind CSS

**Acceptance Criteria:**
- ✅ Clean, professional UI
- ✅ Real-time message display
- ✅ Ship recommendations show images and specs
- ✅ Responsive design (mobile + desktop)

**Deliverable:** `/frontend` - React application

---

### Phase 1 Checkpoint
**Test Scenario:**
1. Visit localhost:3000
2. Start new conversation
3. Type: "I want a solo mining ship under $300"
4. AI responds with questions
5. Answer: "I prefer something versatile"
6. AI recommends: MISC Prospector with reasoning
7. Conversation saved to database

**Success Criteria:** Complete end-to-end flow works reliably

---

## PHASE 2: Voice Integration

### Objective
Replace text input/output with natural voice conversation.

### Tasks

#### 2.1: Speech-to-Text Setup
**Duration:** 2 days  
**Tasks:**
- [ ] Sign up for OpenAI Whisper API
- [ ] Add audio recording to React frontend:
  - Record button
  - Visual feedback (recording indicator)
  - Stop recording
- [ ] Send audio blob to backend
- [ ] Backend: Call Whisper API → transcribe → return text
- [ ] Display transcription in chat

**Acceptance Criteria:**
- ✅ User can record voice
- ✅ Audio transcribed accurately (> 90% accuracy)
- ✅ Transcription appears in chat interface

**Deliverable:** `voice_input.py` + updated frontend

---

#### 2.2: Text-to-Speech Setup
**Duration:** 2 days  
**Tasks:**
- [ ] Sign up for ElevenLabs API
- [ ] Select appropriate voice (professional, friendly)
- [ ] Backend: Send AI response → ElevenLabs → receive audio
- [ ] Stream audio to frontend
- [ ] Frontend: Auto-play AI responses
- [ ] Add audio controls (pause, replay)

**Acceptance Criteria:**
- ✅ AI responses converted to natural-sounding speech
- ✅ Audio plays automatically after AI responds
- ✅ User can replay or pause audio

**Deliverable:** `voice_output.py` + updated frontend

---

#### 2.3: Voice-First UX
**Duration:** 2 days  
**Tasks:**
- [ ] Update UI for voice mode:
  - Large "Talk" button (push-to-talk or continuous)
  - Waveform visualization during recording
  - Auto-scroll during conversation
- [ ] Add voice activity detection (optional)
- [ ] Handle interruptions gracefully
- [ ] Add fallback to text if voice fails

**Acceptance Criteria:**
- ✅ Voice interaction feels natural
- ✅ Visual feedback during all states
- ✅ Graceful error handling

**Deliverable:** Updated frontend with voice-first design

---

#### 2.4: WebSocket Streaming (Stretch Goal)
**Duration:** 3 days  
**Tasks:**
- [ ] Implement WebSocket endpoint for real-time streaming
- [ ] Stream audio chunks from client → server
- [ ] Process transcription in real-time
- [ ] Stream AI audio response back to client
- [ ] Reduce latency to < 2 seconds end-to-end

**Acceptance Criteria:**
- ✅ Near real-time voice conversation
- ✅ Low latency (< 2s response time)
- ✅ Smooth audio playback

**Deliverable:** `/ws/voice` WebSocket implementation

---

### Phase 2 Checkpoint
**Test Scenario:**
1. Visit site
2. Click "Start Voice Consultation"
3. Speak: "I need a versatile ship for exploration and light cargo"
4. AI speaks back: "Great! What's your budget range?"
5. Continue full conversation via voice
6. No typing required

**Success Criteria:** Entire conversation conducted via voice only

---

## PHASE 3: Document Generation

### Objective
Auto-generate professional PDFs after conversation ends.

### Tasks

#### 3.1: Ship Image Management
**Duration:** 1 day  
**Tasks:**
- [ ] Download high-quality ship images from RSI
- [ ] Organize in `/static/ship_images/{ship_slug}.jpg`
- [ ] Update database with image paths
- [ ] Create image optimization script (resize, compress)

**Acceptance Criteria:**
- ✅ Image for every ship in database
- ✅ Optimized file sizes (< 500KB each)
- ✅ Consistent aspect ratios

**Deliverable:** `/static/ship_images/` directory

---

#### 3.2: Transcript PDF Template
**Duration:** 2 days  
**Tasks:**
- [ ] Design PDF layout:
  - Header with logo/branding
  - Conversation transcript (timestamped)
  - User info summary
  - Footer with contact/branding
- [ ] Implement with ReportLab or WeasyPrint
- [ ] Add styling (fonts, colors, spacing)
- [ ] Test with sample conversations

**Acceptance Criteria:**
- ✅ Professional-looking PDF
- ✅ Readable, well-formatted transcript
- ✅ Branded design

**Deliverable:** `generate_transcript_pdf.py`

---

#### 3.3: Fleet Composition Guide PDF
**Duration:** 3 days  
**Tasks:**
- [ ] Design 2-page template:
  - **Page 1:**
    - Recommended ships (name, image, price, specs)
    - Brief reasoning for each
  - **Page 2:**
    - Loadout suggestions per ship
    - Upgrade path recommendations
    - Total fleet cost breakdown
    - Next steps / purchase links
- [ ] Implement with ReportLab/WeasyPrint
- [ ] Insert ship images programmatically
- [ ] Style for print quality

**Acceptance Criteria:**
- ✅ Visually appealing 2-page PDF
- ✅ Ship images render correctly
- ✅ Clear, actionable recommendations

**Deliverable:** `generate_fleet_guide_pdf.py`

---

#### 3.4: PDF Generation Automation
**Duration:** 2 days  
**Tasks:**
- [ ] Detect conversation completion (user says "done", timeout, explicit end)
- [ ] Trigger PDF generation automatically
- [ ] Save PDFs with unique filenames (conversation_uuid)
- [ ] Store PDF paths in database
- [ ] Add error handling (retry on failure)

**Acceptance Criteria:**
- ✅ PDFs generate automatically when conversation ends
- ✅ Both PDFs saved and paths stored in DB
- ✅ Reliable generation (no silent failures)

**Deliverable:** `pdf_automation.py`

---

### Phase 3 Checkpoint
**Test Scenario:**
1. Complete a voice conversation
2. AI says: "I'm generating your fleet recommendations now"
3. Wait 10-15 seconds
4. Check `/outputs/` folder
5. Find two PDFs:
   - `transcript_{uuid}.pdf`
   - `fleet_guide_{uuid}.pdf`
6. Open PDFs → verify professional quality

**Success Criteria:** Both PDFs exist, look professional, contain accurate data

---

## PHASE 4: Email Delivery

### Objective
Automatically email PDFs to user after conversation.

### Tasks

#### 4.1: SendGrid Setup
**Duration:** 1 day  
**Tasks:**
- [ ] Create SendGrid account
- [ ] Get API key
- [ ] Verify sender email domain
- [ ] Test sending basic email from backend

**Acceptance Criteria:**
- ✅ Successfully send test email via SendGrid

**Deliverable:** SendGrid credentials configured

---

#### 4.2: Email Template Design
**Duration:** 1 day  
**Tasks:**
- [ ] Create HTML email template:
  - Subject: "Your Star Citizen Fleet Recommendations"
  - Header with branding
  - Personalized greeting
  - Summary of recommendations
  - Two PDF attachments
  - Footer with links
- [ ] Make mobile-responsive

**Acceptance Criteria:**
- ✅ Professional HTML email
- ✅ Renders correctly in Gmail, Outlook, Apple Mail

**Deliverable:** `email_template.html`

---

#### 4.3: Email Integration
**Duration:** 2 days  
**Tasks:**
- [ ] Add email input to frontend (before or after conversation)
- [ ] Validate email format
- [ ] Backend endpoint: Send email with PDFs attached
- [ ] Add retry logic (3 attempts)
- [ ] Log email status in database
- [ ] Send confirmation: "Check your email!"

**Acceptance Criteria:**
- ✅ User can provide email
- ✅ Email sent successfully with both PDFs attached
- ✅ Email marked as sent in database

**Deliverable:** `email_service.py` + updated frontend

---

### Phase 4 Checkpoint
**Test Scenario:**
1. Complete voice conversation
2. Provide email: test@example.com
3. AI confirms: "I'll email your recommendations to test@example.com"
4. Check inbox within 60 seconds
5. Open email → verify PDFs attached

**Success Criteria:** Email received with both PDFs, professional formatting

---

## PHASE 5: Deployment & Polish

### Objective
Deploy live to public URL, polish UX, create portfolio materials.

### Tasks

#### 5.1: Backend Deployment
**Duration:** 1 day  
**Tasks:**
- [ ] Push code to GitHub
- [ ] Deploy to Render/Railway
- [ ] Set up PostgreSQL database (cloud)
- [ ] Configure environment variables (API keys)
- [ ] Test all endpoints on production

**Acceptance Criteria:**
- ✅ Backend accessible at public URL
- ✅ Database connected and seeded
- ✅ All API endpoints working

**Deliverable:** Live backend API

---

#### 5.2: Frontend Deployment
**Duration:** 1 day  
**Tasks:**
- [ ] Build React app for production
- [ ] Deploy to Vercel/Netlify
- [ ] Connect to production backend
- [ ] Test full user flow on live site

**Acceptance Criteria:**
- ✅ Frontend accessible at public URL
- ✅ Connected to live backend
- ✅ Voice + PDF + email flow works end-to-end

**Deliverable:** Live website

---

#### 5.3: UX Polish
**Duration:** 2 days  
**Tasks:**
- [ ] Add loading states everywhere
- [ ] Improve error messages (user-friendly)
- [ ] Add animations/transitions
- [ ] Mobile optimization
- [ ] Browser testing (Chrome, Safari, Firefox)
- [ ] Accessibility improvements (keyboard navigation, screen readers)

**Acceptance Criteria:**
- ✅ Smooth, polished user experience
- ✅ No jarring transitions or broken states
- ✅ Works on mobile and desktop

**Deliverable:** Polished UI/UX

---

#### 5.4: Branding & Domain (Optional)
**Duration:** 1 day  
**Tasks:**
- [ ] Design logo or wordmark
- [ ] Create favicon
- [ ] Buy domain (e.g., starcitisalesagent.com)
- [ ] Configure DNS
- [ ] Add SSL certificate

**Acceptance Criteria:**
- ✅ Custom domain works
- ✅ HTTPS enabled
- ✅ Branding consistent throughout

**Deliverable:** Branded, custom domain site

---

#### 5.5: Documentation & Portfolio
**Duration:** 2 days  
**Tasks:**
- [ ] Write comprehensive README:
  - Project description
  - Tech stack
  - Features
  - How to run locally
  - API documentation
  - Screenshots
- [ ] Record demo video:
  - 2-3 minute walkthrough
  - Show voice conversation
  - Show PDFs being generated
  - Show email delivery
- [ ] Create portfolio page entry
- [ ] Post on LinkedIn with demo link
- [ ] Add to GitHub with proper tags

**Acceptance Criteria:**
- ✅ Clear, professional README
- ✅ Demo video hosted (YouTube/Vimeo)
- ✅ Portfolio page updated
- ✅ LinkedIn post published

**Deliverable:** Complete portfolio materials

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1: Data + Text AI** | 2-3 weeks | 150+ ships in DB, working text chat |
| **Phase 2: Voice Integration** | 1 week | Full voice conversation capability |
| **Phase 3: PDF Generation** | 1 week | Auto-generated professional PDFs |
| **Phase 4: Email Delivery** | 3 days | Automated email with attachments |
| **Phase 5: Deployment** | 5 days | Live site + portfolio materials |

**Total:** 5-6 weeks (working consistently)

---

## Success Metrics

**Technical:**
- ✅ 150+ ships in database with complete data
- ✅ < 2 second AI response time
- ✅ > 95% voice transcription accuracy
- ✅ 100% email delivery success rate
- ✅ Zero critical bugs in production

**User Experience:**
- ✅ Natural voice conversation flow
- ✅ Relevant ship recommendations
- ✅ Professional PDF quality
- ✅ Email received within 60 seconds

**Portfolio Impact:**
- ✅ Demonstrates full-stack AI capabilities
- ✅ Shows enterprise-level implementation
- ✅ Unique, impressive demo for interviews
- ✅ Deployable, shareable public URL

---

## Risk Management

### Potential Risks & Mitigations

**Risk:** API rate limits or downtime  
**Mitigation:** Cache ship data locally, implement retry logic, have backup data sources

**Risk:** Voice recognition accuracy issues  
**Mitigation:** Always show transcription for user to verify, allow text fallback

**Risk:** PDF generation performance bottlenecks  
**Mitigation:** Generate PDFs asynchronously, add progress indicator, optimize image sizes

**Risk:** Email delivery failures  
**Mitigation:** Retry logic, fallback to download link, log all failures for debugging

**Risk:** API costs exceeding budget  
**Mitigation:** Set usage limits, monitor costs daily, optimize API calls (batch where possible)

---

## Notes for Cursor Claude

**When building with Cursor:**

1. **Start with Phase 1 completely** before adding voice/email
2. **Test each task independently** before moving to next
3. **Use the database schema exactly as specified** - it's designed to scale
4. **Don't skip the data validation steps** - garbage in = garbage out
5. **Keep PDFs simple at first** - can always make them prettier later
6. **Log everything** - you'll need it for debugging
7. **Write tests as you go** - saves time in the long run

**Key files to create:**
- `/backend/main.py` - FastAPI app
- `/backend/ai_consultant.py` - Core AI logic
- `/backend/rag_system.py` - Ship retrieval
- `/backend/pdf_generation.py` - PDF creation
- `/backend/email_service.py` - Email sending
- `/frontend/src/App.jsx` - Main React component
- `/frontend/src/components/VoiceChat.jsx` - Voice interface

**Environment variables you'll need:**
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
SENDGRID_API_KEY=SG...
```

---

## Questions to Resolve During Build

- [ ] Do we want push-to-talk or continuous voice recording?
- [ ] Should we support multiple languages? (Start with English only)
- [ ] Do we want user accounts or anonymous sessions?
- [ ] Should PDFs be downloadable from site or email-only?
- [ ] Do we want conversation history (if user returns)?

**Default answers for MVP:**
- Push-to-talk (simpler)
- English only
- Anonymous (no auth required)
- Email-only (simpler)
- No history (one-time consultations)

Can always add these features later!

---

**END OF SPECIFICATION**

Ready to build. Start with Phase 1, Task 1.1.
Good luck, and remember: ship it, don't perfect it. Get Phase 1 working before worrying about voice or PDFs.
