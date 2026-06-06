# Asura AI

Asura AI is a polished React + TypeScript frontend with a Python FastAPI backend for Gemini-powered chat.

## Project structure

- `src/` — React + TSX application
- `backend/` — FastAPI proxy for Gemini requests
- `backend/.env.example` — sample environment file for Gemini API key

## Setup

### 1. Install frontend dependencies

In the project root:

```bash
npm install
```

### 2. Install backend dependencies

In the `backend` folder:

```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Configure Gemini API key

Copy the example file and add your API key:

```bash
cd backend
copy .env.example .env
# Then edit backend/.env and add your GEMINI_API_KEY
```

### 4. Run the backend

```bash
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 5. Run the frontend

From the project root:

```bash
npm run dev
```

### 6. Open the app

Visit `http://localhost:5173` in your browser.

## Notes

- The frontend proxies requests to `http://127.0.0.1:8000/api/chat`.
- Make sure your Gemini API key is valid and has API access.
- Existing `index.html`, `styles.css`, and `script.js` are preserved but the new React app is now the main UI.
