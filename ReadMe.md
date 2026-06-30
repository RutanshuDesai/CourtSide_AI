# 🎾 CourtSide AI

CourtSide AI is an agentic tennis scheduling assistant that combines calendar availability, weather checks, recovery constraints, and personal notes to help decide when to play.

The repo is primarily an exploration of practical agent design: tool orchestration, constraint-based reasoning, RAG, and observability around a real personal decision-making workflow.

---

## Context

This project started from a repeated real-world problem: evaluating tennis match proposals in a ladder-style tournament. Accepting or proposing a match is not just a calendar check. It usually requires:

- checking Google Calendar availability
- validating weather for the exact place and time
- applying a recovery constraint based on the previous day's workouts
- sometimes comparing several candidate slots across multiple days

That turns a simple decision into a multi-step process with enough moving parts that it becomes tedious and error-prone to do manually.

For the full project story, design rationale, and lessons learned, see the accompanying [Medium post](https://medium.com/@rutanshudesai/building-courtside-ai-what-a-personal-ai-assistant-taught-me-about-agentic-decision-making-d9d722a1488d).

---

## What The App Does

Given a natural-language request such as:

> "Can I play in Cary Saturday at 5 PM, or Holly Springs Sunday at 10 AM?"

the agent can:

- check calendar conflicts across configured calendars
- fetch hourly weather data for the requested slot
- apply recovery constraints from recent activity
- explain whether a slot is playable
- suggest alternatives if a slot fails
- create a Google Calendar event after confirmation
- retrieve relevant personal notes through RAG

There is also an option to auto-fetch the available match proposals and do the analysis. 

---

## App Screenshots

For a quick visual walkthrough of the app, see the screenshots in `app_images/`, which include scheduling flows, calendar integration, weather checks, and match recommendation examples.

---

## Quickstart

### Prerequisites

- Python 3.11+
- Git
- [Ollama](https://ollama.ai) if running locally with local models
- Google Calendar OAuth credentials if you want calendar access
- A World Weather Online API key

### Setup

```bash
git clone https://github.com/RutanshuDesai/CourtSide_AI.git
cd agentic_tennis_app

python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp example.env .env
```

If using Ollama locally:

```bash
ollama pull gemma4:26b
ollama pull nomic-embed-text
```

### Run

```bash
streamlit run tennis_agent_app/app.py
```

The app runs at `http://localhost:8501`.

---

## Required Environment

At minimum, configure these values in `.env`:

| Variable | Purpose |
|----------|---------|
| `MODEL_ENDPOINT` | LLM backend: `ollama`, `vertex`, or `databricks` |
| `EMBEDDING_ENDPOINT` | Embedding backend: `ollama` or `vertex` |
| `WEATHER_API_KEY` | Weather API key |
| `GOOGLE_CALENDAR_CRED_FILE_PATH` | Path to Google OAuth credentials file |
| `GOOGLE_CALENDAR_TOKEN_FILE_PATH` | Path to Google OAuth token file |
| `GOOGLE_CALENDAR_ID` | Primary calendar ID |
| `GOOGLE_CALENDAR_IDS_TO_CHECK` | Comma-separated option to scan mulitple calendars at once to check for conflicts |
| `VECTOR_INDEX_DB_PATH` | Path to the Chroma persist directory |

Backend-specific variables:

- `VERTEX_API_KEY` when using `MODEL_ENDPOINT=vertex`
- `DATABRICKS_TOKEN`, `DATABRICKS_BASE_URL`, and related Databricks settings when using `MODEL_ENDPOINT=databricks`
- `OLLAMA_MODEL` and `OLLAMA_EMBEDDING_MODEL` if you want to override local defaults

Optional:

- `APP_PASSWORD` to gate access to the Streamlit UI
- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT`, `LANGCHAIN_API_KEY` for LangSmith tracing

See `example.env` for the full config surface.

---

## Architecture

The app uses:

- **Streamlit** for the chat interface
- **LangChain `create_agent`** for tool-calling orchestration
- **ChromaDB** for RAG
- **Google Calendar tools** for conflict lookup and event creation
- **World Weather Online** for hourly forecasts

High-level flow:

1. Receive a scheduling request in natural language or auto-fetch available proposals from the tournament.
2. Check calendar conflicts and recent activity.
3. Pull weather data for the requested slot and buffer window.
4. Reason across constraints.
5. Return a verdict and, if the user confirms, create the calendar event.

The current implementation keeps the workflow lightweight by encoding most of the decision logic in the system prompt while using tool calls for external data retrieval.

This is a good fit for an agentic approach because the decision depends on multiple external systems and layered constraints. The app needs to fetch live data, reason across calendar, weather, and recovery rules, compare options, and optionally take an action afterward. That makes a tool-calling agent a better fit than a single-shot LLM response.

---

## Tools

| Tool | Purpose |
|------|---------|
| `list_calendar_events` | Read events across configured calendars |
| `create_calendar_event` | Create a new event after confirmation |
| `get_weather` | Fetch hourly weather for a location and time |
| `retrieve_context` | Search personal notes through RAG |

Current playability checks include:

- temperature between roughly `40°F` and `95°F`
- wind below `10 mph`
- rain probability below `15%`

---

## RAG And Notes

The project can retrieve personal notes such as tennis strategy, training context, or match observations through a local Chroma index.

To build or refresh the index:

```bash
python tennis_agent_app/sample_build_index.py
```

Place source documents in `data/` before indexing.

To inspect the stored collections and chunks, use `tennis_agent_app/vector_index_diagnostics.py`. It lists all collections in the Chroma DB and outputs indexed chunks as a DataFrame for quick verification.

---

## Observability

The codebase currently aligns best with **LangSmith** for tracing. If enabled through the standard `LANGCHAIN_*` environment variables, you can inspect tool calls, inputs, outputs, and final responses.

**Langfuse** is a reasonable alternative if you want self-hosted observability, but that requires hosting Langfuse yourself before wiring it in.

---

## Deployment

The app is containerized and can be deployed to **Google Cloud Run**.

Typical flow:

```bash
./deploy/push_secrets.sh
./deploy/build.sh
./deploy/deploy.sh
```

You will also need GCP configuration in `.env`, including:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_SERVICE_NAME`
- `GCP_AR_REPO`
- `GCP_IMAGE_NAME`

The deployment scripts use Secret Manager for `.env` and Google Calendar credentials.

---

## Future Work

- stronger automated evaluations across prompts and models
- more explicit workflow/state management for reliability
- richer proposal ranking and alternative generation
- better long-term memory and preference handling
- continued deployment and cost tuning
