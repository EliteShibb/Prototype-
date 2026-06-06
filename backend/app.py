import json
import os
from dotenv import load_dotenv
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = os.getenv('GEMINI_MODEL', 'gemini-1.5')

app = FastAPI(title='Asura AI Backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    reply: str


def parse_gemini_response(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ''

    candidate = payload.get('predictions') or payload.get('output') or payload.get('prediction') or payload.get('candidates')
    if isinstance(candidate, dict):
        candidate = [candidate]
    if not candidate:
        return ''

    first = candidate[0]
    if not isinstance(first, dict):
        return ''

    content = first.get('content') or first.get('text') or first.get('output') or first.get('response')
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get('text', ''))
        return ''.join(parts)

    candidates = first.get('candidates')
    if isinstance(candidates, list) and candidates:
        candidate_content = candidates[0].get('content')
        if isinstance(candidate_content, str):
            return candidate_content

    nested_text = first.get('text')
    if isinstance(nested_text, str):
        return nested_text

    return ''


def build_gemini_candidates(prompt: str) -> list[tuple[str, dict]]:
    return [
        (f'https://gemini.googleapis.com/v1/models/{MODEL_NAME}:generate?key={GEMINI_API_KEY}', {
            'input': {'text': prompt},
            'temperature': 0.2,
            'maxOutputTokens': 420,
        }),
        (f'https://gemini.googleapis.com/v1/models/{MODEL_NAME}:predict?key={GEMINI_API_KEY}', {
            'instances': [{'content': prompt}],
            'parameters': {
                'temperature': 0.2,
                'maxOutputTokens': 420,
            },
        }),
        (f'https://gemini.googleapis.com/v1/models:generate?key={GEMINI_API_KEY}', {
            'model': MODEL_NAME,
            'input': {'text': prompt},
            'temperature': 0.2,
            'maxOutputTokens': 420,
        }),
        (f'https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generate?key={GEMINI_API_KEY}', {
            'input': {'text': prompt},
            'temperature': 0.2,
            'maxOutputTokens': 420,
        }),
        (f'https://generativelanguage.googleapis.com/v1/models:generate?key={GEMINI_API_KEY}', {
            'model': MODEL_NAME,
            'input': {'text': prompt},
            'temperature': 0.2,
            'maxOutputTokens': 420,
        }),
    ]


@app.post('/api/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    global GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail='Missing GEMINI_API_KEY in environment. Copy backend/.env.example to backend/.env and add your key.')

    last_detail = None
    for endpoint, payload in build_gemini_candidates(request.prompt):
        body = json.dumps(payload).encode('utf-8')
        req = Request(
            endpoint,
            data=body,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            if exc.code == 404:
                last_detail = f'Gemini endpoint not found: {endpoint}'
                continue
            if exc.code in {400, 422}:
                last_detail = f'Gemini invalid request at {endpoint}: {detail}'
                continue
            raise HTTPException(status_code=502, detail=f'Gemini API error {exc.code}: {detail}')
        except URLError as exc:
            last_detail = f'Gemini request failed for {endpoint}: {exc.reason}'
            continue
        except json.JSONDecodeError as exc:
            last_detail = f'Gemini response decode failure for {endpoint}: {exc}'
            continue

        reply = parse_gemini_response(result)
        if reply:
            return ChatResponse(reply=reply)

        last_detail = f'Gemini returned unexpected response format from {endpoint}.'

    raise HTTPException(status_code=502, detail=last_detail or 'Gemini request failed for all configured endpoints.')
