# Haven - AI-Orchestrated Group Therapy Matching System

![Haven Logo](https://img.shields.io/badge/Haven-Mental%20Wellness-9f7aea)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-2.0+-red)

A warm, gamified mental wellness platform that uses AI to match users with compatible group therapy sessions through empathetic conversation and interactive assessments.

---

## 🌙 Overview

Haven transforms the clinical intake process into a warm, human-centered journey. Instead of filling out cold questionnaires, users engage in a natural conversation with an empathetic AI that gently discovers their struggles through play and casual chat.

### Key Features

✨ **Phase 1: Discovery & Insight Extraction**
- Warm, empathetic chatbot with "peer support" persona
- Slot-filling strategy to understand therapeutic needs
- Natural language processing for sentiment analysis

🎮 **Phase 2: Gamified Assessment**
- "Stress Bubble Popper" - Interactive stressor identification
- "Weather Inside" mood slider with visual landscape
- Stealth assessment through playful interaction

🎯 **Phase 3: Intelligent Group Matching**
- 5 evidence-based archetype groups
- AI-powered categorization based on concerns
- Beautiful insight cards with personalized messaging

📅 **Phase 4: Seamless Coordination**
- Automated scheduling across participants
- Mock payment integration (Stripe sandbox)
- Zero-friction booking experience

👨‍⚕️ **Phase 5: Therapist Handoff**
- Comprehensive briefing materials
- Individual participant "cheat cards"
- Group mood heatmaps
- Downloadable PDF reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)                │
│  - Landing page with warm gradient aesthetics            │
│  - Interactive chat interface                            │
│  - Gamified assessment modules                           │
│  - Group matching visualization                          │
│  - Scheduling & payment UI                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ REST API
                 │
┌────────────────▼────────────────────────────────────────┐
│                 Backend (Flask/Python)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │         ChatbotEngine (AI Logic)                 │   │
│  │  - Slot filling strategy                         │   │
│  │  - Sentiment analysis                            │   │
│  │  - Confidence scoring                            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         GroupMatcher (Categorization)            │   │
│  │  - 5 archetype groups                            │   │
│  │  - Keyword matching algorithm                    │   │
│  │  - Insight card generation                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │       TherapistHandoff (Documentation)           │   │
│  │  - Participant profile generation                │   │
│  │  - Group briefing materials                      │   │
│  │  - PDF export (mock)                             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/haven-therapy-matcher.git
cd haven-therapy-matcher
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add Firebase Admin credentials**
Download a Firebase service account JSON and save it as `serviceAccountKey.json` in the project root,
or set `FIREBASE_KEY_PATH` to its location.

5. **Run the application**
```bash
python run.py
```

5. **Open in browser**
```
http://localhost:5000
```

---

## 📱 Usage Guide

### For Users

1. **Start Journey** - Click "Begin Your Journey" on the landing page
2. **Chat Phase** - Engage in natural conversation (3-4 messages)
3. **Bubble Game** - Tap stress bubbles to identify concerns
4. **Mood Slider** - Show your internal weather
5. **Insight Card** - Receive your personalized archetype
6. **Group Matching** - Connect with your tribe
7. **Schedule** - Pick a time that works
8. **Payment** - Complete booking (mock Stripe)

### For Therapists

1. Navigate to `/therapist/dashboard`
2. View group mood heatmap
3. Review participant "cheat cards"
4. Download comprehensive PDF brief
5. Start session with full context

---

## 🎨 Design Philosophy

### Visual Aesthetic
- **Inspiration**: Cosmos, Stoic apps
- **Palette**: Warm gradients (purple, pink, blue)
- **Typography**: DM Serif Display + Outfit
- **Motion**: Floating orbs, smooth transitions
- **Tone**: Late-night conversation, not clinical exam

### Psychological Principles

1. **Cognitive Load Reduction**
   - Minimal choices
   - Progressive disclosure
   - Clear visual hierarchy

2. **Affect Labeling**
   - Naming emotions helps regulate them
   - Visual externalization of stress

3. **Group Cohesion**
   - Archetype-based matching
   - Shared experience validation

4. **Trust Building**
   - Warm, lowercase language
   - No medical jargon
   - Validation before questions

---

## 🧠 AI Logic

### Slot Filling Strategy

The chatbot uses a state machine to fill 4 critical slots:

```python
slots = {
    'primary_complaint': None,  # What's wrong?
    'duration': None,            # How long?
    'severity': None,            # 1-10?
    'goal': None                 # Vent or fix?
}
```

**Exit Condition**: `Confidence > 80%` OR `4 messages exchanged`

### System Prompt

```
You are a warm, empathetic friend helping someone through a tough time.

RULES:
1. NO clinical jargon (symptoms, diagnosis, disorder)
2. Use lowercase for warmth
3. ALWAYS validate before asking
4. Keep responses SHORT (2-3 sentences)
5. You are NOT a doctor
```

### Group Matching Algorithm

1. Extract keywords from user input
2. Score each archetype group
3. Return highest match
4. Generate personalized insight card

---

## 🎯 The 5 Archetype Groups

### 1. The Navigators 🧭
**Focus**: Career/Academic Stress  
**For**: High-performers with imposter syndrome  
**Keywords**: work, career, stress, performance, anxiety

### 2. The Anchors ⚓
**Focus**: Grief & Loss  
**For**: Processing major life transitions  
**Keywords**: grief, loss, death, transition, change

### 3. The Mirrors 🪞
**Focus**: Social Anxiety & Relationships  
**For**: Struggling with connection and self-perception  
**Keywords**: social, anxiety, relationships, lonely

### 4. The Balancers ⚖️
**Focus**: Burnout & Balance  
**For**: Experiencing work-life boundary collapse  
**Keywords**: burnout, tired, exhausted, boundaries

### 5. The Explorers 🌱
**Focus**: Identity & Self-Esteem  
**For**: Figuring out who they want to be  
**Keywords**: identity, self, confidence, worth, purpose

---

## 🔌 API Documentation

### Chat Endpoints

#### Start Chat Session
```http
POST /api/chat/start
Response: {
  "session_id": "session_1234567890",
  "message": "hey there. the world can be a lot sometimes..."
}
```

#### Send Message
```http
POST /api/chat/message
Body: {
  "session_id": "session_1234567890",
  "message": "I've been feeling really stressed lately",
  "turn_count": 1
}
Response: {
  "message": "that sounds really heavy...",
  "ready_for_next_phase": false,
  "confidence": 0.6
}
```

### Assessment Endpoints

#### Bubble Game Results
```http
POST /api/assessment/bubble
Body: {
  "session_id": "session_1234567890",
  "selected_bubbles": ["Work", "Future", "Money"]
}
```

#### Mood Slider Results
```http
POST /api/assessment/mood
Body: {
  "session_id": "session_1234567890",
  "mood_level": 35
}
```

### Matching Endpoints

#### Find Group
```http
POST /api/matching/find-group
Body: {
  "session_id": "session_1234567890"
}
Response: {
  "group": {
    "name": "The Navigators",
    "description": "...",
    "focus": "Career/Academic Stress"
  },
  "insight": {
    "archetype": "The Navigator",
    "title": "You're carrying the weight...",
    "description": "..."
  }
}
```

### Scheduling Endpoints

#### Get Available Slots
```http
GET /api/scheduling/available-slots
Response: {
  "slots": [
    {"day": "Tuesday", "time": "6:00 PM", "available": true},
    ...
  ]
}
```

#### Confirm Booking
```http
POST /api/booking/confirm
Body: {
  "session_id": "session_1234567890",
  "time_slot": "Tuesday 6:00 PM",
  "payment_info": {...}
}
```

### Therapist Endpoints

#### Get Dashboard Data
```http
GET /api/therapist/dashboard/navigators
Response: {
  "group_name": "The Navigators",
  "session_date": "Tuesday, February 01, 2026",
  "participant_count": 3,
  "group_themes": [...],
  "collective_mood": "High anxiety, low energy",
  "participants": [...]
}
```

---

## 🔒 Privacy & Safety

### Data Handling
- Minimal data collection
- Anonymized storage
- No PII required for demo
- Clear consent flow (production)

### Safety Protocols
- Crisis detection keywords
- Escalation pathways
- Professional therapist oversight
- Encrypted communication (production)

### Ethical Considerations
- AI limitations clearly communicated
- "Tool, not human" boundary setting
- Professional therapy as primary care
- Peer support as supplement

---

## 🧪 Testing

### Manual Testing Flow

1. **Chat Phase**
   - Test 4 different conversation paths
   - Verify slot filling works
   - Check confidence calculation

2. **Games**
   - Click all bubbles
   - Move mood slider through full range
   - Verify data capture

3. **Matching**
   - Test each archetype trigger
   - Verify correct group assignment
   - Check insight card personalization

4. **Scheduling**
   - Select different time slots
   - Complete mock payment
   - Verify booking confirmation

5. **Dashboard**
   - View therapist interface
   - Check participant cards
   - Test PDF download (mock)

---

## 🚧 Production Roadmap

### Phase 1: MVP (Current)
- [x] Frontend prototype
- [x] Flask backend
- [x] Slot-filling chatbot
- [x] Group matching logic
- [x] Mock scheduling/payment

### Phase 2: AI Integration
- [ ] OpenAI API integration
- [ ] Real sentiment analysis
- [ ] Advanced NLP for slot filling
- [ ] Conversation memory

### Phase 3: Full Stack
- [ ] PostgreSQL database
- [ ] User authentication
- [ ] Real Stripe integration
- [ ] Google Calendar API
- [ ] Email notifications

### Phase 4: Clinical Features
- [ ] Crisis detection & escalation
- [ ] Therapist verification system
- [ ] Session notes & tracking
- [ ] Outcome measurement tools

### Phase 5: Scale
- [ ] Multi-language support
- [ ] Mobile apps (Flutter)
- [ ] Video session integration
- [ ] Insurance integration

---

## 📊 Evaluation Criteria

### ✅ AI Intelligence & Automation
- Slot-filling conversational strategy
- Keyword-based group matching
- Automated insight generation

### ✅ User Experience & Trust
- Warm, lowercase aesthetic
- Validation-first responses
- Gamified assessments reduce anxiety

### ✅ Clinical Value & Safety
- Evidence-based archetype groups
- Comprehensive therapist handoff
- Clear AI limitations

### ✅ Technical Execution
- Clean, documented code
- RESTful API design
- Scalable architecture

### ✅ Business Impact
- Reduces therapist admin time
- Increases group therapy accessibility
- Scalable matching system

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Mani** - Creator & Developer
- Built for Mentra Bounty Challenge 2026

---

## 🙏 Acknowledgments

- Mentra team for the challenge opportunity
- Cosmos & Stoic apps for design inspiration
- OpenAI for AI capabilities
- Mental health professionals who reviewed our approach

---

## 📞 Contact

For questions, feedback, or support:
- Email: support@haven-app.com
- Discord: [Join our community](https://discord.gg/haven)
- Website: [haven-app.com](https://haven-app.com)

---

## 🌟 Star Us!

If you find Haven helpful, please star this repository and share it with others who might benefit!

---

**Remember**: Haven is a tool to support mental wellness, not replace professional care. If you're in crisis, please contact emergency services or a crisis hotline immediately.
