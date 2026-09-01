# News NIT IIT – AI Sponsorship Lead Generation & Outreach Automation

> **Owner/Admin**: Instagram page [@news.nit_iit](https://instagram.com/news.nit_iit)  
> **Audience**: Indian College Students (Engineering, IIT/NIT, Medical, University) & Youth Demographic  
> **Media Profile Initial Stats**: `2,500+` Followers | `80 Lakh+` Monthly Views | Strong Presence in `Surat/Gujarat` & Nationwide India

---

## 1. Project Overview

The **News NIT IIT Sponsorship Engine** is an automated, AI-powered lead generation and outreach system designed to convert Instagram reach into a structured sponsorship acquisition pipeline.

Every day, the system dynamically discovers organizations, businesses, startups, creators, services, and brands across India that would benefit from reaching Indian college students and young people through `@news.nit_iit`.

---

## 2. Key Features

- 🎯 **Dynamic Category Discovery**: Uses a **70% exploitation / 30% exploration** strategy to continuously discover unexpected sponsor categories (EdTech, PGs/Housing, Sports Academies, AI/SaaS, Student Travel, Laptops/Gadgets, D2C Apparel, etc.).
- 💯 **100-Point Deterministic Lead Scoring**: Evaluates prospects across 8 key dimensions (Audience relevance 30, Sponsorship potential 20, Overlap 15, Quality 10, Social activity 10, Geo 5, Growth 5, Fit 5) to categorize leads into **HOT**, **HIGH**, **MEDIUM**, and **LOW** tiers.
- 💬 **Data-Verified DM Personalization**: Generates professional, human-sounding outreach messages citing exact, non-fabricated `MEDIA_PROFILE` stats and specific observations about each business.
- 🛡️ **Multi-Field Deduplication**: Prevents duplicate DMs by matching Instagram handles, domain names, emails, phone numbers, and business names.
- 🛑 **Dry-Run & Approval Safeguards**: Ships with `DRY_RUN=true` and `APPROVAL_REQUIRED=true` to protect platform reputation and guarantee human approval before any DM is sent.
- 📊 **Dual Storage & Streamlit Dashboard**: Syncs automatically with 5 Google Sheets (`LEADS`, `MEDIA_PROFILE`, `OUTREACH`, `SEARCH_HISTORY`, `ANALYTICS`) with seamless SQLite local offline fallback.

---

## 3. Project Architecture

```
Insta-Sponser/
├── config/
│   ├── settings.py           # Environment variables & system limits
│   └── media_profile.py      # Configurable @news.nit_iit statistics profile
├── app/
│   ├── database/
│   │   ├── models.py         # Pydantic data schemas (Lead, SearchHistory, Outreach)
│   │   ├── sqlite_db.py      # Local SQLite database manager & persistent cache
│   │   └── sheets.py         # Google Sheets sync client (5 worksheets)
│   ├── discovery/
│   │   ├── category_generator.py # 70/30 exploration-exploitation category engine
│   │   ├── search_engine.py      # Web search integration (DuckDuckGo / Search API)
│   │   └── candidate_finder.py   # Raw lead candidate collection & filtering
│   ├── research/
│   │   ├── company_research.py   # Full candidate research consolidator
│   │   ├── instagram_research.py # Public Instagram handle research
│   │   └── website_research.py   # Website contact & growth signal extraction
│   ├── scoring/
│   │   └── lead_scorer.py        # 100-point lead evaluation engine & tiering
│   ├── personalization/
│   │   ├── collaboration_generator.py # Tailored collaboration proposals
│   │   └── message_generator.py       # Custom outreach DM generator
│   ├── outreach/
│   │   ├── approval.py       # Human review & lead approval workflow
│   │   ├── followup.py       # Day 4-7 and Day 10-14 follow-up cadence
│   │   └── instagram_sender.py # Dry-Run simulation & Meta API sender
│   ├── analytics/
│   │   └── analytics.py      # Pipeline metrics, conversion rates, city stats
│   ├── utils/
│   │   ├── logging.py        # Console & file logging
│   │   ├── validation.py     # Input normalization & handle formatting
│   │   └── deduplication.py  # Multi-field duplicate detection
│   └── scheduler/
│       └── daily_job.py      # 12-step daily pipeline orchestrator
├── dashboard/
│   └── app.py                # Interactive Streamlit Dashboard UI
├── tests/                    # Unit tests for scoring, dedup, validation, messages
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py                   # Main CLI entry point
└── README.md
```

---

## 4. Setup & Configuration

### Prerequisites
- Python 3.9+
- Virtual environment (`venv` or `conda`)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` as needed:
```ini
DRY_RUN=true
APPROVAL_REQUIRED=true
LOG_LEVEL=INFO
DAILY_OUTREACH_LIMIT=5
```

---

## 5. Third-Party Integrations Setup

### 1. Google Sheets Setup (Optional but Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a Service Account.
2. Generate and download the JSON key.
3. Paste the contents into `GOOGLE_SHEETS_CREDENTIALS_JSON` in `.env`.
4. Create a Google Sheet, copy its ID from the URL, and paste it into `GOOGLE_SHEET_ID`.
5. Share the Google Sheet with the service account email.

*Note: If Google Sheets credentials are omitted, the application automatically runs in SQLite mode.*

### 2. Meta / Instagram Graph API Configuration
For live outreach (Phase 3):
1. Obtain an approved Meta Developer App and Business Access Token.
2. Populate `META_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID` in `.env`.
3. Keep `DRY_RUN=true` during testing. Set `DRY_RUN=false` only when ready.

---

## 6. How to Run

### Command Line Interface (CLI)

1. **Run Daily Lead Discovery Pipeline**:
```bash
python main.py run-daily
```
*Executes the 12-step daily process, generates top leads, saves them to DB/Google Sheets, and prints the formatted Top-5 Daily Report.*

2. **Launch Streamlit Dashboard**:
```bash
python main.py dashboard
```
*Opens interactive web UI at `http://localhost:8501` to view lead metrics, review/approve DMs, edit MEDIA_PROFILE, and monitor pipeline performance.*

3. **Run Unit Test Suite**:
```bash
pytest
```

---

## 7. Roadmap & Phased Execution

### Phase 1 (Built & Verified):
- [x] Project architecture & data models
- [x] Configurable `MEDIA_PROFILE`
- [x] SQLite & Google Sheets dual database layer
- [x] Dynamic 70/30 category generator
- [x] Search & candidate discovery engine
- [x] Multi-identifier deduplication engine
- [x] 100-Point deterministic lead scoring & tiering
- [x] Personalized DM generator using verified stats
- [x] 12-step daily pipeline orchestrator & Top-5 report
- [x] Full pytest suite

### Phase 2 (Built & Verified):
- [x] Streamlit Dashboard UI (`dashboard/app.py`)
- [x] Human approval queue interface
- [x] Follow-up cadence scheduler
- [x] Category & location analytics

### Phase 3 (Future Meta API Live Outreach):
- [ ] Meta Developer Portal App Review approval
- [ ] Live Instagram Direct Messaging via Graph API
- [ ] Automatic DM response classification & CRM webhooks

---

## 8. Compliance & Security Safeguards

1. **Privacy First**: Only collects publicly available business information. No private personal data or credentials are harvested.
2. **Platform Rules**: Does not bypass CAPTCHAs, rate limits, or authentication security controls.
3. **No Mass Spam**: Enforces conservative daily outreach caps (`DAILY_OUTREACH_LIMIT=5`).
