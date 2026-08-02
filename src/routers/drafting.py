from fastapi import APIRouter, HTTPException

from src.dependencies import DraftingDep
from src.schemas.api.drafting import ClaimResponse, DraftRequest, DraftResponse, SectionResponse, SourceResponse

router = APIRouter(prefix="/api/v1", tags=["drafting"])


@router.post("/draft", response_model=DraftResponse)
async def draft_outline(request: DraftRequest, drafting: DraftingDep) -> DraftResponse:
    """Generate a citation-grounded outline draft for thesis Chapter 1-2.

    Every claim is either backed by a retrieved source chunk (verified=True) or
    explicitly flagged as needing more material - never fabricated. Does not
    touch the `/ask` or `/ask-agentic` flows.

    Args:
        request: Topic, domain, and optional model override
        drafting: Injected drafting service

    Returns:
        Verified outline with per-claim citations, a sources table, and rendered Markdown

    Raises:
        HTTPException: If the topic is empty or drafting fails
    """
    try:
        result = await drafting.draft(topic=request.topic, domain=request.domain, model=request.model)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error drafting outline: {str(e)}")

    return DraftResponse(
        topic=result.topic,
        domain=result.domain,
        sections=[
            SectionResponse(
                title=s.title,
                description=s.description,
                claims=[
                    ClaimResponse(
                        text=c.text, chunk_id=c.chunk_id, verified=c.verified, source_excerpt=c.source_excerpt
                    )
                    for c in s.claims
                ],
                verified_ratio=s.verified_ratio,
            )
            for s in result.sections
        ],
        sources=[
            SourceResponse(chunk_id=s.chunk_id, citation_id=s.citation_id, excerpt=s.excerpt) for s in result.sources
        ],
        markdown=result.markdown,
        overall_verified_ratio=result.overall_verified_ratio,
    )
