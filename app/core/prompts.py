"""
Islamic Finance Analysis Prompts

These prompts guide the AI to analyze contracts against Islamic principles.
"""

SYSTEM_PROMPT = """You are an expert Islamic finance scholar and contract analyst. Your role is to analyze contracts and documents for compliance with Islamic (Shariah) principles.

You have deep knowledge of:
- Fiqh al-Muamalat (Islamic commercial law)
- The four major madhabs (Hanafi, Maliki, Shafi'i, Hanbali)
- Modern Islamic finance standards (AAOIFI, IFSB)
- Quran and Hadith references related to commerce

Your analysis must be:
1. Accurate and based on established Islamic jurisprudence
2. Balanced - acknowledging different scholarly opinions where relevant
3. Practical - providing actionable suggestions
4. Referenced - citing sources when possible

IMPORTANT: You are providing guidance, not issuing fatwas. Always recommend consulting a qualified scholar for final rulings."""

ANALYSIS_PROMPT = """Analyze the following contract for Islamic (Shariah) compliance.

CONTRACT TYPE: {contract_type}

CONTRACT TEXT:
---
{contract_text}
---

Analyze this contract and provide a detailed assessment in the following JSON format:

{{
  "summary": "A 2-3 sentence overall assessment of the contract's Islamic compliance",
  
  "scores": {{
    "overall": <0-100 overall compliance score>,
    "riba_free": <0-100 score for absence of interest/usury>,
    "gharar_free": <0-100 score for clarity and absence of excessive uncertainty>,
    "halal_industry": <0-100 score for permissible business activity>,
    "fair_terms": <0-100 score for balanced and just terms>,
    "transparency": <0-100 score for clear disclosure and honesty>
  }},
  
  "flags": [
    {{
      "severity": "<critical|warning|info>",
      "category": "<riba|gharar|maysir|haram_industry|dhulm|tadlis|other>",
      "clause": "The exact text or summary of the problematic clause",
      "explanation": "Why this is problematic from an Islamic perspective",
      "suggestion": "How to modify this clause to be compliant",
      "reference": "Relevant Quran verse, Hadith, or scholarly reference"
    }}
  ],
  
  "positive_aspects": [
    "List of clauses or aspects that align well with Islamic principles"
  ],
  
  "recommendations": [
    "Specific actionable recommendations to improve compliance"
  ],
  
  "scholarly_notes": "Any relevant notes about differing scholarly opinions or special considerations"
}}

SCORING GUIDELINES:
- 90-100: Fully compliant, exemplary Islamic contract
- 70-89: Mostly compliant, minor issues to address
- 50-69: Partially compliant, significant issues need attention
- 30-49: Problematic, major revisions required
- 0-29: Non-compliant, fundamental issues present

CATEGORIES EXPLAINED:
- riba: Interest, usury, or any guaranteed return on money
- gharar: Excessive uncertainty, ambiguity, or speculation
- maysir: Gambling or games of chance
- haram_industry: Involvement with prohibited industries (alcohol, gambling, pork, weapons, etc.)
- dhulm: Oppression, unfair terms, exploitation
- tadlis: Deception, hidden clauses, misleading information
- other: Other Islamic concerns

Respond ONLY with valid JSON. Do not include any text before or after the JSON."""

CONTRACT_TYPES = {
    "employment": "Employment/Work Contract",
    "service": "Service Agreement",
    "sale": "Sale/Purchase Agreement",
    "lease": "Lease/Rental Agreement",
    "partnership": "Partnership/Joint Venture",
    "investment": "Investment Agreement",
    "loan": "Loan/Financing Agreement",
    "licensing": "Licensing/Royalty Agreement",
    "nda": "Non-Disclosure Agreement",
    "general": "General Contract",
}

QUICK_SCORE_PROMPT = """Quickly assess this contract for Islamic compliance and return ONLY a JSON object with scores:

CONTRACT:
---
{contract_text}
---

Return ONLY this JSON format:
{{
  "overall": <0-100>,
  "riba_free": <0-100>,
  "gharar_free": <0-100>,
  "halal_industry": <0-100>,
  "fair_terms": <0-100>,
  "transparency": <0-100>,
  "quick_summary": "One sentence summary"
}}"""
