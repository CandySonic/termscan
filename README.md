# Halal Contract API

An AI-powered API that analyzes contracts against Islamic finance principles and ethical guidelines.

## 🕌 What It Does

1. **Analyze contracts** for Islamic compliance
2. **Score permissibility** (0-100 scale)
3. **Flag violations** (Riba, Gharar, Haram industries, etc.)
4. **Suggest improvements** with scholarly references
5. **Generate reports** (JSON or PDF)

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

## 📊 Response Example

```json
{
  "id": "contract_abc123",
  "status": "completed",
  "scores": {
    "overall": 85,
    "riba_free": 100,
    "gharar_free": 70,
    "halal_industry": 100,
    "fair_terms": 85,
    "transparency": 80
  },
  "flags": [
    {
      "severity": "warning",
      "category": "gharar",
      "clause": "Payment terms subject to market conditions",
      "explanation": "Ambiguous payment terms may constitute gharar (excessive uncertainty)",
      "suggestion": "Specify exact payment amounts and dates",
      "reference": "Sahih Muslim 1513"
    }
  ],
  "summary": "This contract is largely compliant with Islamic principles..."
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
