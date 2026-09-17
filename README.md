# OpportunityIQ

**AI Opportunity Intelligence Agent**

> Discover. Verify. Analyze. Act.

OpportunityIQ is an AI-powered career intelligence platform that combines live web search, profile-aware matching, skill-gap analysis, and explainable recommendations to help students and early-career professionals find and evaluate opportunities.

---

## Problem

Career opportunities — internships, entry-level jobs, research positions — are scattered across dozens of websites and change frequently. Students waste hours searching manually, comparing listings, checking eligibility, and guessing whether an opportunity actually matches their skills.

There is no single tool that:
- Searches live, current opportunities across the web
- Understands the student's profile and skills
- Compares opportunities against their background
- Identifies exactly what skills are missing
- Explains why each opportunity is relevant
- Provides actionable next steps

## Solution

OpportunityIQ acts as an **intelligent career research assistant** that:

1. **Understands your profile** — Upload a resume or enter your skills manually.
2. **Searches live opportunities** — Uses SerpApi to search current web information in real-time.
3. **Extracts structured data** — Normalizes opportunities into comparable, structured records.
4. **Matches to your profile** — Transparent, weighted scoring against your skills, experience, and preferences.
5. **Analyzes skill gaps** — Shows exactly what you have, what you need, and what to learn first.
6. **Explains recommendations** — Every result includes a clear explanation of why it's relevant to you.
7. **Cites sources** — Every factual claim links back to its origin. Nothing is fabricated.

## Key Features

- **Live Web Search** — Real-time search using SerpApi (Google Jobs, Google Search, Google News)
- **AI Agent Workflow** — Plan → Search → Extract → Match → Analyze → Report
- **Resume Understanding** — Upload PDF/DOCX/TXT or enter profile manually
- **Structured Opportunity Extraction** — Position, company, location, skills, eligibility, and more
- **Profile-Aware Matching** — Weighted scoring: Skills (50%), Experience (20%), Education (10%), Location (10%), Preferences (10%)
- **Skill Gap Analysis** — Missing skills, priority ranking, preparation recommendations
- **RAG** — Retrieval-augmented generation for profile context
- **Source Verification** — Every result traceable to its origin
- **Follow-up Questions** — Refine results conversationally
- **Search History & Saved Opportunities** — Track and revisit your research

## Why SerpApi

SerpApi is not an add-on — it is the core data source that makes OpportunityIQ possible.

Without SerpApi, the system would rely on static datasets or manual scraping, both of which produce stale, unreliable results. Career opportunities change daily: new positions open, deadlines pass, requirements update.

OpportunityIQ uses SerpApi to:
- **Search Google Jobs** for structured job/internship listings
- **Search Google** for supplementary information, company context, and application pages
- **Search Google News** for recent announcements and hiring trends

The AI agent decides which search sources are relevant for each query, ensuring efficient and targeted API usage.

## Architecture

```
┌─────────────────────┐
│      Streamlit      │
│      Frontend       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Application Layer  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     AI Planner      │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌────────┐
│SerpApi │  │Profile │
│ Tools  │  │ / RAG  │
└───┬────┘  └───┬────┘
    │           │
    └─────┬─────┘
          ▼
┌─────────────────────┐
│ Matching + Analysis │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│    LLM Reasoning    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Final AI Report    │
└─────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Language | Python 3.11+ |
| Search | SerpApi |
| LLM | Google Gemini (configurable to OpenAI) |
| Agent | LangGraph |
| RAG | FAISS + sentence-transformers |
| Data Models | Pydantic v2 |
| Document Parsing | PyPDF2, python-docx |
| Configuration | python-dotenv |
| Testing | pytest |

## Project Structure

```
opportunityiq/
├── app.py                    # Streamlit entry point
├── config.py                 # Configuration management
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
├── agent/                    # AI agent orchestration
│   ├── graph.py              # LangGraph workflow
│   ├── state.py              # Agent state models
│   ├── planner.py            # Search planning
│   └── prompts.py            # System prompts
├── tools/                    # Search tool abstractions
│   ├── serpapi_tools.py      # SerpApi wrapper
│   ├── search_tools.py       # High-level search
│   └── extraction_tools.py   # Result extraction
├── rag/                      # RAG pipeline
│   ├── embeddings.py         # Embedding model
│   ├── vectorstore.py        # FAISS store
│   ├── retriever.py          # Retrieval logic
│   └── documents.py          # Document processing
├── profile/                  # User profile
│   ├── parser.py             # Resume parsing
│   ├── models.py             # Profile models
│   └── matcher.py            # Profile matching
├── analysis/                 # Opportunity analysis
│   ├── opportunity.py        # Opportunity model
│   ├── scoring.py            # Match scoring
│   ├── skill_gap.py          # Skill gap analysis
│   └── ranking.py            # Ranking logic
├── ui/                       # Streamlit UI
│   ├── styles.py             # CSS design system
│   ├── components.py         # Reusable components
│   └── pages.py              # Page renderers
├── utils/                    # Utilities
│   ├── logger.py             # Logging
│   ├── validators.py         # Input validation
│   └── helpers.py            # Helpers
├── data/
│   └── sample_profile.json   # Demo data
└── tests/                    # Test suite
```

## Installation

```bash
# Clone the repository
git clone https://github.com/24cs73-prince/Serpapi-ai-opportunity-agent-hackathon.git
cd opportunityiq

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|----------|-------------|
| `SERPAPI_API_KEY` | Your SerpApi key ([get one](https://serpapi.com/)) |
| `LLM_API_KEY` | Gemini or OpenAI API key |
| `LLM_PROVIDER` | `gemini` or `openai` |
| `MODEL_NAME` | Model identifier (e.g., `gemini-2.0-flash`) |

## Running Locally

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

## Testing

```bash
pytest tests/
```

## Limitations

- Opportunity data is only as current as the web search results at query time.
- Match scores are profile-to-opportunity similarity indicators, not hiring probability predictions.
- Information that cannot be found in search results is explicitly marked as unavailable — never fabricated.
- SerpApi usage is subject to your API plan's rate limits.

## Future Improvements

- Multi-language support
- Opportunity alerts and notifications
- Collaborative comparison features
- Integration with application tracking systems
- Enhanced company research and culture analysis

## Hackathon Track

**AI Agents** — SerpApi India Hackathon 2026

## License

MIT License — see [LICENSE](LICENSE).
