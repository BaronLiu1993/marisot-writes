# Docs AI Backend

FastAPI backend for an AI-powered writing assistant Chrome extension. Uses Claude to analyze documents and generate improvement plans and edits.

## Setup

```bash
make setup   # start MongoDB + Redis + install dependencies
make dev     # run server at http://localhost:8000
make down    # stop MongoDB
```

## Async File Ingestion (Celery)

Start worker:

```bash
venv/bin/celery -A queues.file.fileIngestionWorker.celery_app worker --loglevel=info
```

Queue module to enqueue tasks:

- [queues/file/fileIngestionQueue.py](queues/file/fileIngestionQueue.py)
- Worker task:
	- [queues/file/fileIngestionWorker.py](queues/file/fileIngestionWorker.py)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/plan` | Analyze a document and return an improvement plan |
| POST | `/agent` | Execute a plan step and return concrete text edits |
| GET | `/health` | Health check |
