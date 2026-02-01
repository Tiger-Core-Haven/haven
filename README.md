# Haven — AI‑Guided Group Matching for Mental Wellness
# haven.mathengeinc.com

## 🎥 Demo + Presentation
- [Client demo video](https://drive.google.com/file/d/12ok1UGJ40jl6IZLkbWRn8BeLjnhu7Hl6/view?usp=sharing)
- [Presentation (PDF)](https://drive.google.com/file/d/1CrR1t1HrqowSkskrR6Es4P3RNedIlv17/view?usp=sharing)



![Haven Logo](https://img.shields.io/badge/Haven-Mental%20Wellness-9f7aea)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Flask](https://img.shields.io/badge/flask-3.x-red)

Haven is a warm, gamified mental‑wellness experience that uses conversational AI and playful reflection to match users with a supportive small group. It runs as a Flask app with Firebase Auth + Firestore, Gemini (google‑genai), and Resend transactional email.

---

## 🌙 What the app does

**User flow**
1) Google sign‑in (Firebase)
2) Calm chat with AI (Gemini) to collect intent + context
3) Two short reflections (bubble stressors + mood slider)
4) Group match + insight card
5) Time slot selection + booking
6) Confirmation email + calendar (.ics)
7) Client summary + **My Group** page

**Therapist flow**
- Therapists are users with `role = "therapist"` in Firestore
- They can open the **Therapist Dashboard** from the navbar
- Dashboard aggregates session summaries + participant insights

---

## ✨ Key features

- **Conversational AI** via Gemini (`google-genai`) with structured output
- **Firebase Auth** (Google sign‑in) + **Firestore** storage
- **Gamified assessments** (stress bubble popper + mood slider)
- **Group matching** into archetype‑based cohorts
- **Transactional email** via Resend (welcome, match, booking)
- **Calendar support** with downloadable `.ics`
- **Client “My Group” page** with session details + captured data
- **Therapist dashboard** with role‑based access

---

## 🧱 Architecture

```
Frontend (Flask templates + JS)
  └── Landing + chat + games + booking + client summary
Backend (Flask API)
  ├── /api/chat/*  (chat, assessment, match, booking)
  ├── /api/auth/*  (Firebase sync + role)
  └── /api/chat/session/* (summary + calendar)
Services
  ├── Firebase Auth + Firestore
  ├── Gemini (google-genai)
  └── Resend (transactional email)
```

---

## ✅ Quick start (local)

### Prereqs
- Python **3.10+** (3.11 recommended)
- Firebase Admin service account JSON
- Resend API key (optional if MAIL_ENABLED=false)
- Google AI API key (Gemini)

### Install
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure
Create a `.env` or export environment variables:

```bash
export FIREBASE_KEY_PATH=./serviceAccountKey.json
export GOOGLE_API_KEY=your_gemini_api_key
export MAIL_ENABLED=false
export APP_BASE_URL=http://localhost:5000
```

Optional (if sending email):
```bash
export MAIL_ENABLED=true
export RESEND_API_KEY=your_resend_key
export MAIL_FROM="Haven <no-reply@mail.haven.mathengeinc.com>"
export MAIL_REPLY_TO=support@haven.mathengeinc.com
```

### Run
```bash
python run.py
```
Open: `http://localhost:5000`

---

## 🌐 Production (Render)

Use the provided `.env.render` as a template. Start command:
```bash
gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

Make sure `APP_BASE_URL` is set to your live domain so emails + calendar links resolve correctly.

---

## 🔐 Roles

To make a user a therapist, set their Firestore user doc:

```
Collection: users
Document ID: <firebase uid>
Field: role = "therapist"
```

---

## 📨 Emails sent today

- **Welcome** (on first login)
- **Group match** (when match is created)
- **Booking confirmation** (includes `.ics` calendar link)

You can add more triggers in `app/ai/routes.py` and new templates in `app/email/templates/`.

---

## 📅 Calendar support

When a booking is confirmed, the app generates a downloadable `.ics` file:
```
GET /api/chat/session/calendar/<booking_id>.ics
```

Timezone is captured from the client (`Intl.DateTimeFormat().resolvedOptions().timeZone`) and stored with the booking/session.

---

## 🔌 API endpoints (current)

### Auth
- `POST /api/auth/sync`

### Chat
- `POST /api/chat/start`
- `POST /api/chat/message`

### Assessments
- `POST /api/chat/assessment/bubble`
- `POST /api/chat/assessment/mood`

### Matching + booking
- `POST /api/chat/match`
- `GET  /api/chat/scheduling/available-slots`
- `POST /api/chat/booking/confirm`

### Session summaries + calendar
- `GET /api/chat/session/summary/<session_id>`
- `GET /api/chat/session/summary/latest`
- `GET /api/chat/session/calendar/<booking_id>.ics`

### Therapist
- `GET /api/chat/therapist/dashboard/<group_id>`
- `GET /api/chat/therapist/download-brief/<group_id>` (mock)

---

## 📄 Pages

- `/` — main onboarding flow
- `/my-group` — client summary + session info
- `/privacy` — privacy policy
- `/terms` — terms of service

---

## 🧪 Notes

- The “payment” step is **UI‑only (mock)**
- Therapist “Download brief” is a **mock** endpoint
- This is a wellness support app and **not a medical provider**

---

## 🧩 Tech stack

- **Flask** (API + templates)
- **Firebase Auth + Firestore**
- **Gemini (google‑genai)** for AI chat
- **Resend** for transactional email
- **Render** for hosting (recommended)
- **Cloudflare** for DNS

---

## 📄 License

MIT License — see `LICENSE`.
