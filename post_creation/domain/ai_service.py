import os
import re
import json
import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

# Ensure you set GEMINI_API_KEY in your env
client = genai.Client() if os.environ.get("GEMINI_API_KEY") else None

EMPIRICAL_MARKERS = [
    r'\d+%', r'percent', r'study', r'research', r'data', r'according to', r'cited', r'figure', 
    r'table', r'https?://', r'report', r'analysis shows', r'evidence', r'correlation', r'causation'
]

def requires_grounding(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(marker, text_lower) for marker in EMPIRICAL_MARKERS)


async def generate_embedding(text: str) -> Optional[List[float]]:
    if not client or len(text) < 15:
        return None
    try:
        # Note: We run it in a thread or we use async client if google-genai supports it.
        # google-genai 1.0+ supports async via client.aio
        response = await client.aio.models.embed_content(
            model='text-embedding-004',
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Embedding generation error: {e}")
        return None

def calculate_dqs(data: dict, grounding_chunks: Optional[List[dict]] = None) -> dict:
    t = data.get('toulmin', {})
    c = 1 if t.get('claim') else 0
    g = 1 if t.get('grounds') else 0
    w = 1 if t.get('warrant') else 0
    b = 1 if t.get('backing') else 0
    q = 1 if t.get('qualifier') else 0
    r = 1 if t.get('rebuttal') else 0

    w_g, w_w, w_b, w_q, w_r = 1.5, 1.0, 0.8, 0.5, 1.2
    ASQ = (c + (g * w_g) + (w * w_w) + (b * w_b) + (q * w_q) + (r * w_r)) / (1 + w_g + w_w + w_b + w_q + w_r)

    fallacies = data.get('fallacies', [])
    FS = max(0.0, 1.0 - (len(fallacies) * 0.15))

    gr = data.get('grice', {})
    CPS = (gr.get('quality', 0) + gr.get('quantity', 0) + gr.get('relevance', 0) + gr.get('manner', 0)) / 4.0

    I = data.get('sentimentIntensity', 0.5)
    ETS = 1.0 - (I * (1.0 - ASQ))

    W_a, W_f, W_c, W_e = 0.35, 0.25, 0.25, 0.15
    DQS_Decimal = (W_a * ASQ) + (W_f * FS) + (W_c * CPS) + (W_e * ETS)
    score = round(DQS_Decimal * 100)

    verified_sources = []
    if grounding_chunks:
        for chunk in grounding_chunks:
            web = chunk.get('web')
            if web and web.get('uri'):
                verified_sources.append({'uri': web.get('uri'), 'title': web.get('title') or web.get('uri')})

    return {
        'score': score,
        'scores': {
            'ASQ': round(ASQ * 100),
            'FS': round(FS * 100),
            'CPS': round(CPS * 100),
            'ETS': round(ETS * 100)
        },
        'toulmin': t,
        'fallacies': fallacies,
        'grice': gr,
        'sentimentIntensity': I,
        'reasoning': data.get('reasoning'),
        'suggestion': data.get('suggestion'),
        'tags': data.get('tags'),
        'constructive': data.get('constructive'),
        'verifiedSources': verified_sources if verified_sources else None
    }

async def analyze_post_content(text: str, is_video_caption: bool = False) -> dict:
    if not client:
        return _mock_analysis()

    try:
        needs_grounding = requires_grounding(text)
        tools = [{'google_search': {}}] if needs_grounding else None

        prompt = f"""
      Analyze social media post. Output JSON.
      1. Verify claims via Search ONLY if necessary.
      2. Identify Toulmin structure & Fallacies.
      3. Suggest 1 actionable improvement.
      Text: "{text}"
        """
        
        response = await client.aio.models.generate_content(
            model='gemini-3.0-flash', # Or gemini-3-flash-preview depending on exact availability
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                # Hardcoding the schema properties since google-genai relies on Pydantic or manual dict
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "toulmin": {
                            "type": "OBJECT",
                            "properties": {
                                "claim": {"type": "BOOLEAN"},
                                "grounds": {"type": "BOOLEAN"},
                                "warrant": {"type": "BOOLEAN"},
                                "backing": {"type": "BOOLEAN"},
                                "qualifier": {"type": "BOOLEAN"},
                                "rebuttal": {"type": "BOOLEAN"}
                            }
                        },
                        "fallacies": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "grice": {
                            "type": "OBJECT",
                            "properties": {
                                "quality": {"type": "NUMBER"},
                                "quantity": {"type": "NUMBER"},
                                "relevance": {"type": "NUMBER"},
                                "manner": {"type": "NUMBER"}
                            }
                        },
                        "sentimentIntensity": {"type": "NUMBER"},
                        "reasoning": {"type": "STRING"},
                        "suggestion": {"type": "STRING"},
                        "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "constructive": {"type": "BOOLEAN"}
                    },
                    "required": ["toulmin", "fallacies", "grice", "sentimentIntensity", "reasoning", "suggestion", "tags", "constructive"]
                },
                tools=tools,
                temperature=0.1
            )
        )

        raw_data = json.loads(response.text)
        grounding_chunks = None
        if response.candidates and response.candidates[0].grounding_metadata:
             # Just passing an empty list or manual extraction if needed, in SDK it's mostly for display
             grounding_chunks = []
             if hasattr(response.candidates[0].grounding_metadata, 'grounding_chunks'):
                 for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                     if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                         grounding_chunks.append({'web': {'uri': chunk.web.uri, 'title': chunk.web.title}})
        
        return calculate_dqs(raw_data, grounding_chunks)
    except Exception as e:
        print(f"Gemini analysis failed: {e}")
        return _mock_analysis()


async def analyze_post_topic(content: str, existing_topics: List[str]) -> str:
    if not client: return "General"
    try:
        prompt = f'Classify content: "{content}". Options: {", ".join(existing_topics)} or New.'
        response = await client.aio.models.generate_content(
            model='gemini-3.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {"topic": {"type": "STRING"}}
                }
            )
        )
        return json.loads(response.text).get('topic', 'General')
    except Exception:
        return "General"


async def analyze_post_relationships(source_content: str, targets: List[Dict[str, Any]]) -> Dict[str, str]:
    if not client or not targets:
        return {}
        
    rel_map = {}
    candidates_for_llm = []

    for t in targets:
        sim = t.get('similarity')
        if sim and sim > 0.92:
            rel_map[t['id']] = 'CORROBORATION'
        elif sim and sim < 0.65:
            pass # ignore
        else:
            candidates_for_llm.append(t)
            
    if not candidates_for_llm:
        return rel_map

    try:
        targets_json = json.dumps([{"id": c['id'], "content": c['content'][:200]} for c in candidates_for_llm])
        prompt = f"""
            Task: Classify rhetorical relationship of Targets relative to Source.
            Source: "{source_content[:400]}..."
            Targets: {targets_json}
            
            Types:
            1. EXPANSION (Broadens scope)
            2. CORROBORATION (Supports claim)
            3. CHALLENGE (Disagrees)
            4. NUANCE (Adds conditions)
            5. SYNTHESIS (Combines ideas)
            6. PREREQUISITE (Foundational)
        """
        
        response = await client.aio.models.generate_content(
            model='gemini-3.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "relationships": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "id": {"type": "STRING"},
                                    "type": {"type": "STRING"}
                                }
                            }
                        }
                    }
                },
                temperature=0.0
            )
        )
        
        res_json = json.loads(response.text)
        for r in res_json.get('relationships', []):
            rel_map[r['id']] = r['type']
            
        return rel_map
    except Exception as e:
        print(f"Relationship Analysis Failed: {e}")
        return rel_map

def _mock_analysis() -> dict:
    return {
        'score': 50,
        'scores': {'ASQ': 50, 'FS': 100, 'CPS': 50, 'ETS': 50},
        'toulmin': {'claim': True, 'grounds': False, 'warrant': False, 'backing': False, 'qualifier': False, 'rebuttal': False},
        'fallacies': [],
        'grice': {'quality': 0.5, 'quantity': 0.5, 'relevance': 0.5, 'manner': 0.5},
        'sentimentIntensity': 0.2,
        'reasoning': "AI Analysis unavailable.",
        'suggestion': "Try adding more evidence.",
        'tags': ["Unverified"],
        'constructive': True
    }
