OUTLINE_PROMPT = """You are helping a graduate student draft the outline for Chapter 1 (Introduction) and \
Chapter 2 (Literature Review / Theoretical Basis) of a thesis in {domain_label}.

Topic: {topic}

Produce an outline of 4 to 8 sections that together form a coherent Chapter 1 and Chapter 2 for this thesis. \
For each section give a short title and a one-to-two sentence description of what it should cover.

Respond in JSON format matching this shape:
{{"topic": "...", "sections": [{{"title": "...", "description": "..."}}]}}"""


SECTION_DRAFT_PROMPT = """You are drafting the section "{section_title}" ({section_description}) of a thesis in \
{domain_label}.

You may ONLY use the source excerpts below. Every claim you write MUST be grounded in one of these excerpts.

### Source excerpts:
{context}

### Instructions:
- Write 3 to 6 claims (short paragraphs or sentences) that build out this section using ONLY the excerpts above.
- For each claim, set "chunk_id" to the exact chunk_id of the excerpt that supports it.
- If you cannot support a necessary point with any excerpt, still include the claim but set "chunk_id" to null. \
Do NOT invent a chunk_id and do NOT fabricate content beyond the excerpts.
- Cite sources using {citation_style}.

Respond in JSON format matching this shape:
{{"claims": [{{"text": "...", "chunk_id": "..." or null}}]}}"""
