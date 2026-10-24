# AI Travel Assistant

A RAG-based travel assistant. Upload travel guide PDFs, then ask for itineraries, hotels, food and activities. Answers are built only from passages retrieved from your own guides, in the language you choose from the sidebar. The chat model is **a model served by Groq (`openai/gpt-oss-120b` by default)**.

## Features

- **Upload PDF guides.** Pages are parsed, split into chunks, embedded and stored in Qdrant.
- **Grounded answers.** The model is told to use only the retrieved passages. If the guides do not cover the question, the assistant says so and offers to answer from general knowledge.
- **Follow-up questions.** Vague questions such as "what about food there?" are rewritten into standalone queries using the chat history.
- **Reply language from the sidebar.** The dropdown decides the language of the answer. Non-English questions are translated to English for searching.
- **Spelling and name cleanup.** Typos are corrected and variants such as "srilanka" are normalised before searching.
- **Switchable LLM.** Groq by default; set `MODEL_PROVIDER=openai` to use OpenAI instead.

## How it works

```
Upload    PDF -> PyMuPDF (text per page) -> split (500 chars, 100 overlap)
              -> OpenAI embeddings -> Qdrant

Question  text -> translate to English if needed
               -> spell-correct (the model)
               -> rewrite vague follow-ups (the model)
               -> normalise place names -> embed -> Qdrant top 10
               -> keep strong matches
               -> strict document prompt -> the model 3.3 70B (Groq) -> answer
```

A chunk is kept only if the best match scores at least 0.70 and the chunk scores at least 85 percent of the best score (never below 0.70). If nothing passes, or the model replies `NO_PDF_CONTEXT`, no answer is generated and the UI offers the general-knowledge option.

## Where the Groq model is used

All model calls go through one place, `build_llm()` in `src/generator.py`:

| Call | Temperature | Purpose |
| --- | --- | --- |
| `llm` | 0.7 | Final answer (document mode and general-knowledge mode), query translation, spelling correction |
| `rewrite_llm` | 0 | Follow-up query rewriting |

Groq has no embeddings API, so embeddings still use OpenAI `text-embedding-ada-002` (1536 dimensions). You need both a Groq key and an OpenAI key.

## Tech stack

| Layer | Technology |
| --- | --- |
| Front end | Streamlit |
| Backend | FastAPI, Uvicorn |
| Vector database | Qdrant (cosine distance, 1536 dimensions) |
| Embeddings | OpenAI `text-embedding-ada-002` |
| Chat model | `openai/gpt-oss-120b` on Groq (`langchain-groq`) |
| Orchestration | LangChain (prompts, conversation memory) |
| PDF parsing | PyMuPDF |

## Project structure

```
ai-travel-assistant/
├── app.py              # Streamlit front end
├── requirements.txt
├── start.sh            # Starts backend + front end in one service (Render)
├── .env.example        # Copy to .env and fill in
└── src/
    ├── main.py         # FastAPI app and routes
    ├── config.py       # Environment variables and model settings
    ├── ingest.py       # PDF parsing, chunking, embedding, upload
    ├── embeddings.py   # OpenAI embedding calls
    ├── vectorstores.py # Qdrant client and collection management
    ├── retriever.py    # Search and relevance filtering
    └── generator.py    # LLM setup, rewrite, prompts, answers, memory
```

## Getting started

### Prerequisites

- Python 3.10 or 3.11
- A Groq API key from console.groq.com
- An OpenAI API key (embeddings only)
- A Qdrant instance: Qdrant Cloud, or locally with `docker run -p 6333:6333 qdrant/qdrant`

### 1. Install

```bash
git clone https://github.com/<your-username>/ai-travel-assistant.git
cd ai-travel-assistant
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes (Groq mode) | Groq API key |
| `GROQ_MODEL` | No | Default `openai/gpt-oss-120b`. Any chat model your Groq key can use |
| `MODEL_PROVIDER` | No | `groq` (default) or `openai` |
| `OPENAI_API_KEY` | Yes | Used for embeddings (and chat if `MODEL_PROVIDER=openai`) |
| `OPENAI_CHAT_MODEL` | No | Default `gpt-3.5-turbo`, used only in OpenAI mode |
| `QDRANT_HOST` | Yes | Qdrant URL, for example `https://xyz.qdrant.io:6333` |
| `QDRANT_API_KEY` | Cloud only | Qdrant API key |
| `COLLECTION_NAME` | No | Default `travel_guides` |
| `FASTAPI_URL` | No | Default `http://localhost:8000` |

Never commit `.env`; it is listed in `.gitignore`.

### 3. Run

Backend:

```bash
uvicorn src.main:app --reload
```

Front end, in a second terminal:

```bash
streamlit run app.py
```

Open http://localhost:8501. The API docs are at http://localhost:8000/docs.

## Using the app

1. In the sidebar, upload one or more PDF guides.
2. Choose the reply language from the dropdown.
3. Ask a question, then ask follow-ups.
4. If the guides do not cover the question, choose whether to answer from general knowledge.

| Button | What it does | PDFs kept? |
| --- | --- | --- |
| Clear Chat | Clears this session's chat memory | Yes |
| Clear DB | Deletes and recreates the Qdrant collection | No |

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ask` | Body: `query`, `session_id`, `language`, `use_general`. Returns `response` (null when the guides do not cover it), `rewritten_query`, `has_pdf_context` |
| `POST` | `/upload` | Upload one PDF as multipart form field `file` |
| `POST` | `/clear` | Clear chat memory for a `session_id` |
| `POST` | `/clear-db` | Empty the collection |

No API key is needed for these endpoints, so do not expose the backend publicly without adding authentication.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Sri Lanka", "session_id": "demo", "language": "English"}'
```

## Deploy on Render (single service)

`start.sh` runs FastAPI on `127.0.0.1:8000` (private) and Streamlit on Render's public port, so one service and one URL are enough. The backend is never exposed to the internet.

1. Push the repo to GitHub (without `.env`).
2. In Render choose **New → Web Service** and connect the repo.
3. Set:
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `bash start.sh`
4. Add environment variables: `GROQ_API_KEY`, `OPENAI_API_KEY`, `QDRANT_HOST`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `MODEL_PROVIDER=groq`, `PYTHON_VERSION=3.11.9`. Do not set `FASTAPI_URL`; it defaults to the private backend.
5. Deploy and open the service URL.

Free-plan notes: the service sleeps after about 15 minutes idle and the first request takes 30 to 60 seconds, so open the URL a few minutes before a demo. Chat memory is lost on restart; uploaded PDFs stay in Qdrant.

## Notes and limits

- Groq retired `llama-3.3-70b-versatile` and `llama-3.1-8b-instant` for free and developer accounts on 16 August 2026. If you see a `model_not_found` error, set `GROQ_MODEL` to a model listed at console.groq.com/docs/models.
- Chat memory is held in the server's RAM and is lost on restart.
- Scanned PDFs without a text layer produce no text; OCR is not included.
- Groq's free tier has rate limits. If you hit one, wait a moment or switch `MODEL_PROVIDER=openai`.

## Author

Anusha Sundaramurthi
