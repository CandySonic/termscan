"""
Contract Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional

from app.core.security import get_api_key, get_optional_api_key
from app.models.contract import (
    ContractAnalyzeRequest,
    ContractAnalysis,
    ContractSubmitResponse,
    ScoreOnlyResponse,
    ContractFlag,
    ErrorResponse,
)
from app.services.analyzer import analyzer

router = APIRouter(prefix="/contracts", tags=["Contracts"])

# In-memory storage for MVP (replace with database)
analyses_db: dict = {}


@router.post(
    "/analyze",
    response_model=ContractAnalysis,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
    summary="Analyze a contract",
    description="Submit contract text for full Islamic compliance analysis. Returns scores, flags, and recommendations.",
)
async def analyze_contract(
    request: ContractAnalyzeRequest,
    client: dict = Depends(get_api_key),
):
    """
    Analyze a contract for Islamic (Shariah) compliance.
    
    - **text**: The contract text to analyze (50-100,000 characters)
    - **type**: Type of contract (employment, service, sale, etc.)
    - **language**: Language code (default: en)
    
    Returns detailed analysis with:
    - Overall compliance score (0-100)
    - Category scores (riba, gharar, etc.)
    - Flagged issues with explanations
    - Recommendations for improvement
    """
    try:
        analysis = await analyzer.analyze(
            contract_text=request.text,
            contract_type=request.type,
        )
        
        # Store for later retrieval
        analyses_db[analysis.id] = analysis
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post(
    "/analyze/quick",
    response_model=ScoreOnlyResponse,
    summary="Quick score a contract",
    description="Get a quick compliance score without full analysis. Faster but less detailed.",
)
async def quick_score_contract(
    request: ContractAnalyzeRequest,
    client: dict = Depends(get_api_key),
):
    """
    Get a quick compliance score for a contract.
    
    This is faster than full analysis but provides less detail.
    Use for initial screening before full analysis.
    """
    try:
        result = await analyzer.quick_score(contract_text=request.text)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick score failed: {str(e)}",
        )


@router.get(
    "/{contract_id}",
    response_model=ContractAnalysis,
    responses={
        404: {"model": ErrorResponse, "description": "Contract not found"},
    },
    summary="Get analysis by ID",
    description="Retrieve a previously completed contract analysis by its ID.",
)
async def get_contract_analysis(
    contract_id: str,
    client: dict = Depends(get_api_key),
):
    """
    Retrieve a contract analysis by ID.
    
    Use this to fetch results of a previously analyzed contract.
    """
    analysis = analyses_db.get(contract_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract analysis '{contract_id}' not found",
        )
    
    return analysis


@router.get(
    "/{contract_id}/score",
    response_model=ScoreOnlyResponse,
    summary="Get scores only",
    description="Get just the compliance scores for a contract analysis.",
)
async def get_contract_scores(
    contract_id: str,
    client: dict = Depends(get_api_key),
):
    """
    Get just the scores from a contract analysis.
    
    Useful when you only need the numerical scores.
    """
    analysis = analyses_db.get(contract_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract analysis '{contract_id}' not found",
        )
    
    return ScoreOnlyResponse(
        id=analysis.id,
        scores=analysis.scores,
        quick_summary=analysis.summary,
    )


@router.get(
    "/{contract_id}/flags",
    response_model=list[ContractFlag],
    summary="Get flagged issues",
    description="Get just the flagged issues from a contract analysis.",
)
async def get_contract_flags(
    contract_id: str,
    client: dict = Depends(get_api_key),
):
    """
    Get just the flagged issues from a contract analysis.
    
    Useful when you only need to see the problems.
    """
    analysis = analyses_db.get(contract_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract analysis '{contract_id}' not found",
        )
    
    return analysis.flags
