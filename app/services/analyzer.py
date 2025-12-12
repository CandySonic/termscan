"""
AI-powered contract analyzer service - Multi-Category System
"""
import json
import uuid
import asyncio
from typing import Optional, List
from datetime import datetime

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPTS, ANALYSIS_PROMPTS, SYSTEM_PROMPT, ANALYSIS_PROMPT, QUICK_SCORE_PROMPT
from app.models.contract import (
    ContractAnalysis,
    ContractScores,
    CategoryScores,
    ContractFlag,
    ContractType,
    CheckCategory,
    FlagSeverity,
    FlagCategory,
    ScoreOnlyResponse,
)


class ContractAnalyzer:
    """Analyzes contracts using AI for Islamic compliance"""
    
    def __init__(self):
        self.provider = settings.ai_provider
        self._client = None
    
    @property
    def client(self):
        """Lazy load AI client"""
        if self._client is None:
            if self.provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(api_key=settings.openai_api_key)
            elif self.provider == "anthropic":
                from anthropic import Anthropic
                self._client = Anthropic(api_key=settings.anthropic_api_key)
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self._client = genai.GenerativeModel(settings.ai_model)
            elif self.provider == "groq":
                from groq import Groq
                self._client = Groq(api_key=settings.groq_api_key)
        return self._client
    
    async def analyze(
        self,
        contract_text: str,
        contract_type: ContractType = ContractType.GENERAL,
        checks: List[CheckCategory] = None,
    ) -> ContractAnalysis:
        """
        Perform full analysis of a contract with multiple check categories
        
        Args:
            contract_text: The contract text to analyze
            contract_type: Type of contract for context
            checks: List of check categories to perform
            
        Returns:
            ContractAnalysis with scores, flags, and recommendations
        """
        if checks is None:
            checks = [CheckCategory.ISLAMIC]
        
        analysis_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        # Analyze each category in parallel
        tasks = [
            self._analyze_category(contract_text, contract_type, check)
            for check in checks
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_flags = []
        all_positives = []
        all_recommendations = []
        category_scores = []
        summaries = []
        
        # Legacy scores for backward compatibility (if Islamic is checked)
        legacy_scores = {}
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            
            check = checks[i]
            data = result
            
            # Add category score
            category_scores.append(CategoryScores(
                category=check,
                overall=data.get("score", 50),
                breakdown=data.get("breakdown", {})
            ))
            
            # If Islamic, also populate legacy scores
            if check == CheckCategory.ISLAMIC:
                breakdown = data.get("breakdown", {})
                legacy_scores = {
                    "riba_free": breakdown.get("riba_free", 50),
                    "gharar_free": breakdown.get("gharar_free", 50),
                    "halal_industry": breakdown.get("halal_industry", 50),
                    "fair_terms": breakdown.get("fair_terms", 50),
                    "transparency": breakdown.get("transparency", 50),
                }
            
            # Collect flags
            for flag_data in data.get("flags", []):
                try:
                    # Try to map category string to enum
                    cat_str = flag_data.get("category", "other")
                    try:
                        cat = FlagCategory(cat_str)
                    except ValueError:
                        cat = FlagCategory.OTHER
                    
                    all_flags.append(ContractFlag(
                        severity=FlagSeverity(flag_data.get("severity", "info")),
                        category=cat,
                        clause=flag_data.get("clause", ""),
                        explanation=flag_data.get("explanation", ""),
                        suggestion=flag_data.get("suggestion", ""),
                        reference=flag_data.get("reference"),
                    ))
                except (ValueError, KeyError):
                    continue
            
            all_positives.extend(data.get("positive_aspects", []))
            all_recommendations.extend(data.get("recommendations", []))
            summaries.append(f"**{check.value.replace('_', ' ').title()}:** {data.get('summary', '')}")
        
        # Calculate overall score (average of all category scores)
        overall_score = 50
        if category_scores:
            overall_score = sum(cs.overall for cs in category_scores) // len(category_scores)
        
        # Build combined scores
        scores = ContractScores(
            overall=overall_score,
            riba_free=legacy_scores.get("riba_free"),
            gharar_free=legacy_scores.get("gharar_free"),
            halal_industry=legacy_scores.get("halal_industry"),
            fair_terms=legacy_scores.get("fair_terms"),
            transparency=legacy_scores.get("transparency"),
            categories=category_scores,
        )
        
        return ContractAnalysis(
            id=analysis_id,
            status="completed",
            created_at=datetime.utcnow(),
            contract_type=contract_type,
            summary="\n\n".join(summaries) if summaries else "Analysis completed.",
            scores=scores,
            flags=all_flags,
            positive_aspects=all_positives,
            recommendations=all_recommendations,
            scholarly_notes=None,
        )
    
    async def _analyze_category(
        self,
        contract_text: str,
        contract_type: ContractType,
        check: CheckCategory,
    ) -> dict:
        """Analyze contract for a single category"""
        prompt_template = ANALYSIS_PROMPTS.get(check.value, ANALYSIS_PROMPT)
        system_prompt = SYSTEM_PROMPTS.get(check.value, SYSTEM_PROMPT)
        
        prompt = prompt_template.format(
            contract_type=contract_type.value,
            contract_text=contract_text[:50000],
        )
        
        response_text = await self._call_ai(prompt, system_prompt)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return self._extract_json(response_text)
    
    async def quick_score(
        self,
        contract_text: str,
    ) -> ScoreOnlyResponse:
        """
        Get a quick score without full analysis
        
        Args:
            contract_text: The contract text to score
            
        Returns:
            ScoreOnlyResponse with just scores
        """
        analysis_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        prompt = QUICK_SCORE_PROMPT.format(
            contract_text=contract_text[:20000],
        )
        
        response_text = await self._call_ai(prompt)
        
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            data = self._extract_json(response_text)
        
        scores = ContractScores(
            overall=data.get("overall", 50),
            riba_free=data.get("riba_free", 50),
            gharar_free=data.get("gharar_free", 50),
            halal_industry=data.get("halal_industry", 50),
            fair_terms=data.get("fair_terms", 50),
            transparency=data.get("transparency", 50),
        )
        
        return ScoreOnlyResponse(
            id=analysis_id,
            scores=scores,
            quick_summary=data.get("quick_summary", "Quick analysis completed."),
        )
    
    async def _call_ai(self, prompt: str, system_prompt: str = None) -> str:
        """Call the AI provider with optional custom system prompt"""
        if system_prompt is None:
            system_prompt = SYSTEM_PROMPT
            
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return response.content[0].text
        elif self.provider == "gemini":
            full_prompt = f"{system_prompt}\n\n{prompt}"
            response = self.client.generate_content(full_prompt)
            return response.text
        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
            )
            return response.choices[0].message.content
    
    def _extract_json(self, text: str) -> dict:
        """Try to extract JSON from text that may have extra content"""
        # Find JSON boundaries
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        # Return empty dict if extraction fails
        return {}


# Singleton instance
analyzer = ContractAnalyzer()
