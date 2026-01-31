# 🚀 QUICK START GUIDE - Haven

## Get Running in 3 Minutes

### Option 1: View the Prototype Immediately (No Setup)

1. Open `app/core/core_templates/haven-app.html` in any modern browser
2. Click "Begin Your Journey"
3. Experience the full user flow!

**Note**: This opens the UI only. For chat + matching + booking APIs, run the backend (Option 2).

---

### Option 2: Run Full Stack (Backend + Frontend)

#### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Run the Backend
```bash
python run.py
```

Backend will start at: `http://localhost:5000`

#### Step 3: Open Frontend
Navigate to: `http://localhost:5000`

---

## What You Can Do

### User Journey
1. ✨ **Landing** - Click "Begin Your Journey"
2. 💬 **Chat** - Have a warm conversation (3-4 messages)
3. 🫧 **Bubble Game** - Pop stress bubbles
4. 🌤️ **Mood Slider** - Show your internal weather
5. 🎯 **Insight Card** - Get your archetype
6. 👥 **Group Match** - Find your tribe
7. 📅 **Schedule** - Pick a time
8. 💳 **Payment** - Mock Stripe checkout
9. 👨‍⚕️ **Dashboard** - See therapist view (scroll down after payment)

### Try Different Paths
- Type different concerns in chat ("I'm stressed about work" vs "I feel lonely")
- Click different bubbles to see matching change
- Move mood slider to different positions
- Select different time slots

---

## File Structure

```
haven-therapy-matcher/
├── app/                         # Flask app package
│   └── core/core_templates/     # Main frontend template (standalone too)
├── app.py                       # Flask entrypoint
├── run.py                       # Dev runner
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
├── PRESENTATION.md              # Presentation deck content
├── LICENSE                      # MIT license
└── QUICKSTART.md                # This file
```

---

## Key Features to Show

### 🎨 Design (Inspired by Cosmos & Stoic)
- Warm gradient backgrounds with floating orbs
- DM Serif Display + Outfit fonts
- Smooth animations and transitions
- Lowercase, warm conversational tone

### 🤖 AI Logic
- Slot-filling chatbot strategy
- Sentiment analysis (mock in demo)
- Group matching algorithm
- Personalized insight generation

### 🎮 Gamification
- Interactive bubble popper
- Dynamic mood landscape
- Visual stress externalization
- Non-verbal communication

### 👨‍⚕️ Therapist Tools
- Group mood heatmap
- Individual participant cards
- Comprehensive briefing
- PDF download (mock)

---

## For the Hackathon Demo

### 8-Minute Video Demo Flow:
1. **00:00-00:30** - Problem statement
2. **00:30-01:00** - Landing page walkthrough
3. **01:00-02:30** - Chat interaction
4. **02:30-03:30** - Gamified assessments
5. **03:30-04:30** - Insight & matching
6. **04:30-05:30** - Scheduling & payment
7. **05:30-07:00** - Therapist dashboard
8. **07:00-08:00** - Technical architecture & impact

### Live Demo Tips:
- Have 3-4 pre-written messages ready
- Show different user paths (stressed vs anxious)
- Highlight the warm tone vs clinical feel
- Demo therapist dashboard last
- End with the "why it matters"

---

## Troubleshooting

### Issue: Port 5000 already in use
**Solution**: 
```bash
# Change port in app.py line 407:
app.run(debug=True, port=5001)
```

### Issue: Module not found
**Solution**:
```bash
pip install --upgrade flask flask-cors
```

### Issue: Frontend not loading
**Solution**: 
- Just open `haven-app.html` directly in browser
- No backend needed for basic demo

---

## Next Steps After Hackathon

1. **Integrate Real AI**:
   - OpenAI API for chatbot
   - HuggingFace for sentiment analysis
   
2. **Add Database**:
   - PostgreSQL for user data
   - Store conversation history
   
3. **Real Integrations**:
   - Stripe payment processing
   - Google Calendar API
   - Email notifications

4. **Beta Testing**:
   - Partner with 3-5 therapists
   - 50 real users
   - Collect feedback

---

## Resources

- **Challenge**: mentra-challenge.pdf
- **Starter Pack**: mentra-starter-pack.pdf
- **Full README**: README.md
- **Presentation**: PRESENTATION.md

---

## Contact & Support

Questions during judging?
- Point to README.md for technical details
- Show PRESENTATION.md for business case
- Demo haven-app.html for experience

---

**Good luck! You've got this! 🌙**
