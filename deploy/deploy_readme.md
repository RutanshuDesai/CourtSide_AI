# Deployment Guide — Cloud Run

## Prerequisites

- `gcloud` CLI installed and authenticated (`gcloud auth login`)
- GCP project with Artifact Registry, Cloud Run, and Secret Manager APIs enabled
- `.env` file populated with all required variables (see `example.env`)
- `vertex_db/` index built locally via `production_indexing_vertex.py`
- Google Calendar OAuth token generated locally (`google_secret/token.json`)

## Deployment Order

Run all scripts from the **project root** directory.

### 1. Push Secrets

```bash
./deploy/push_secrets.sh
```

Uploads to GCP Secret Manager:
- `.env` → `agentic_env` (all app config and API keys)
- `google_secret/credentials2.json` → `google-calendar-creds`
- `google_secret/token.json` → `google-calendar-token`

Also grants the Cloud Run service account `secretAccessor` role and sets a 24h version-destroy TTL on `google-calendar-token` and `agentic_env` to prevent old version accumulation.

### 2. Build Image

```bash
./deploy/build.sh
```

Submits source to Cloud Build which:
- Uploads project files (respects `.gcloudignore` — includes `vertex_db/`, excludes `.env`)
- Builds the Docker image
- Pushes to Artifact Registry at `{REGION}-docker.pkg.dev/{PROJECT}/{REPO}/{IMAGE}:latest`

### 3. Deploy to Cloud Run

```bash
./deploy/deploy.sh
```

Deploys the image to Cloud Run with:
- Secret mount: `/secrets/.env` ← `agentic_env:latest`
- Env var overrides: `RUNTIME_ENV=cloud`, `GCP_PROJECT_ID`, `VECTOR_INDEX_DB_PATH=/app/tennis_agent_app/vertex_db`

## How Config Works at Runtime

| Variable | Local | Cloud Run |
|---|---|---|
| `DOTENV_PATH` | not set (uses `.env` via `find_dotenv`) | `/secrets/.env` (mounted secret) |
| `VECTOR_INDEX_DB_PATH` | absolute local path in `.env` | overridden via `--set-env-vars` in `deploy.sh` |
| `RUNTIME_ENV` | not set (defaults to `local`) | `cloud` (set via `--set-env-vars`) |
| Google Calendar creds | local JSON files | fetched from Secret Manager at runtime |

`load_dotenv(override=False)` ensures Cloud Run env vars take precedence over values in the mounted `.env` file.

## Key Files

| File | Purpose |
|---|---|
| `.gcloudignore` | Controls what Cloud Build uploads (allows `vertex_db/`, blocks `.env`) |
| `.dockerignore` | Controls Docker build context |
| `.gitignore` | Controls what goes to git (blocks `vertex_db/` and `.env`) |
| `Dockerfile` | Container definition (Python 3.11 + Playwright + Streamlit) |

## Local Testing (Podman)

```bash
./deploy/run_podman.sh
```

Builds and runs the container locally on port 8501 with `.env` passed directly.
