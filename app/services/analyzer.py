"""
AI-powered contract analyzer service
"""
import json
import uuid
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT, QUICK_SCORE_PROMPT
from app.models.contract import (
    ContractAnalysis,
    ContractScores,
    ContractFlag,
    ContractType,
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
    ) -> ContractAnalysis:
        """
        Perform full analysis of a contract
        
        Args:
            contract_text: The contract text to analyze
            contract_type: Type of contract for context
            
        Returns:
            ContractAnalysis with scores, flags, and recommendations
        """
        analysis_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        # Build the prompt
        prompt = ANALYSIS_PROMPT.format(
            contract_type=contract_type.value,
            contract_text=contract_text[:50000],  # Limit text length
        )
        
        # Call AI
        response_text = await self._call_ai(prompt)
        
        # Parse response
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            data = self._extract_json(response_text)
        
        # Build response
        scores = ContractScores(
            overall=data.get("scores", {}).get("overall", 50),
            riba_free=data.get("scores", {}).get("riba_free", 50),
            gharar_free=data.get("scores", {}).get("gharar_free", 50),
            halal_industry=data.get("scores", {}).get("halal_industry", 50),
            fair_terms=data.get("scores", {}).get("fair_terms", 50),
            transparency=data.get("scores", {}).get("transparency", 50),
        )
        
        flags = []
        for flag_data in data.get("flags", []):
            try:
                flags.append(ContractFlag(
                    severity=FlagSeverity(flag_data.get("severity", "info")),
                    category=FlagCategory(flag_data.get("category", "other")),
                    clause=flag_data.get("clause", ""),
                    explanation=flag_data.get("explanation", ""),
                    suggestion=flag_data.get("suggestion", ""),
                    reference=flag_data.get("reference"),
                ))
            except (ValueError, KeyError):
                continue
        
        return ContractAnalysis(
            id=analysis_id,
            status="completed",
            created_at=datetime.utcnow(),
            contract_type=contract_type,
            summary=data.get("summary", "Analysis completed."),
            scores=scores,
            flags=flags,
            positive_aspects=data.get("positive_aspects", []),
            recommendations=data.get("recommendations", []),
            scholarly_notes=data.get("scholarly_notes"),
        )
    
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
    
    async def _call_ai(self, prompt: str) -> str:
        """Call the AI provider"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
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
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return response.content[0].text
        elif self.provider == "gemini":
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
            response = self.client.generate_content(full_prompt)
            return response.text
        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
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
