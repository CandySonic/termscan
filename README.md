# TermScan - AI Contract Compliance API

An AI-powered API that analyzes contracts against multiple compliance frameworks with a checkbox-based UI.

## 🔍 What It Does

1. **Analyze contracts** for multiple compliance types (user selects via checkboxes)
2. **Score compliance** (0-100 scale per category)
3. **Flag violations** with explanations and suggestions
4. **Provide recommendations** with references
5. **Parallel processing** - analyze multiple categories simultaneously

## ✅ Check Categories

| Category | Icon | What It Checks |
|----------|------|----------------|
| **Islamic Compliance** | 🕌 | Riba (interest), Gharar (uncertainty), Haram industries |
| **Artist Rights** | 🎵 | Royalties, ownership, creative control, termination rights |
| **Privacy & Data** | 🔒 | GDPR, data collection, sharing, consent, retention |
| **Legal Red Flags** | ⚖️ | Non-competes, liability, indemnification, jurisdiction |
| **Fair Terms** | ⚡ | Hidden fees, auto-renewal, one-sided clauses |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your OPENAI_API_KEY or ANTHROPIC_API_KEY

# Run the API
uvicorn app.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/contracts/analyze` | Submit contract for analysis |
| GET | `/v1/contracts/{id}` | Get full analysis |
| GET | `/v1/contracts/{id}/score` | Get scores only |
| GET | `/v1/contracts/{id}/flags` | Get flagged clauses |
| GET | `/v1/contracts/{id}/report.pdf` | Download PDF report |

## 🔑 Authentication

All API requests require an API key in the header:

```
Authorization: Bearer your_api_key_here
```

## 📊 Request Example

```json
{
  "text": "This Employment Agreement is entered into between...",
  "type": "employment",
  "checks": ["islamic", "artist_rights", "fair_terms"]
}
```

## 📊 Response Example

```json
{
  "id": "contract_abc123",
  "status": "completed",
  "scores": {
    "overall": 78,
    "categories": [
      {
        "category": "islamic",
        "overall": 85,
        "breakdown": {
          "riba_free": 100,
          "gharar_free": 70,
          "halal_industry": 100
        }
      },
      {
        "category": "artist_rights",
        "overall": 65,
        "breakdown": {
          "ownership_retained": 50,
          "royalty_fairness": 70,
          "termination_rights": 75
        }
      }
    ]
  },
  "flags": [
    {
      "severity": "warning",
      "category": "ownership",
      "clause": "All works created shall be work-for-hire...",
      "explanation": "Artist loses ownership of their creative work",
      "suggestion": "Negotiate for co-ownership or licensing instead",
      "reference": "Industry standard: artists retain master ownership"
    }
  ],
  "summary": "**Islamic:** Compliant with minor issues.\n\n**Artist Rights:** Concerns with ownership terms."
}
```

## 🏗️ Tech Stack

- **FastAPI** - Python web framework
- **OpenAI/Claude** - AI analysis
- **PostgreSQL** - Database
- **Redis** - Caching & rate limiting
- **PyMuPDF** - PDF text extraction

## 📁 Project Structure

```
halal-contract-api/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── api/
│   │   ├── v1/
│   │   │   ├── contracts.py # Contract endpoints
│   │   │   └── auth.py      # Authentication
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # API key validation
│   │   └── prompts.py       # AI prompts
│   ├── services/
│   │   ├── analyzer.py      # AI analysis logic
│   │   ├── pdf_parser.py    # PDF extraction
│   │   └── report.py        # PDF report generation
│   ├── models/
│   │   └── contract.py      # Pydantic models
│   └── db/
│       └── database.py      # Database connection
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 📜 Islamic Principles Checked

| Principle | Arabic | Description |
|-----------|--------|-------------|
| Riba | ربا | Interest/usury - strictly prohibited |
| Gharar | غرر | Excessive uncertainty in terms |
| Maysir | ميسر | Gambling/speculation |
| Haram Industries | حرام | Forbidden sectors (alcohol, gambling, etc.) |
| Dhulm | ظلم | Oppression/unfair terms |
| Tadlis | تدليس | Deception/hidden clauses |

## 🤝 Integration Example (Laravel/PHP)

```php
$response = Http::withToken(config('services.halal_api.key'))
    ->post('https://api.halalcontract.com/v1/contracts/analyze', [
        'text' => $contract->content,
        'type' => 'employment',
    ]);

$score = $response['scores']['overall'];
```

## 📄 License

Proprietary - Candy Sonic LLC
