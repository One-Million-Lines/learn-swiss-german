# Learn Swiss German

Learn Swiss German is a learning app for exploring Swiss German topics, subtopics, conversations, patterns, vocabulary, and daily practice prompts. It combines a React frontend, static JSON learning content, and a small FastAPI backend for daily phrase and dialogue endpoints.

## What it does

It helps learners browse structured Swiss German study material and practice with topic-based conversations and vocabulary.

## Why it exists

Swiss German resources are often fragmented or inconsistent. This project packages curated learning content into a browsable app with topic grouping, repeatable content structure, and lightweight API support.

## Features

- Topic overview pages
- Subtopic and conversation pages
- Patterns and vocabulary sections
- Daily phrase and daily dialogue endpoints
- Static JSON content served directly during frontend development
- Separate backend API for content endpoints

## How it works

1. The frontend loads most learning content from `data-json/` through the Vite dev server plugin.
2. `frontend/src/lib/api.ts` combines static JSON reads with API calls.
3. The backend exposes `/content/*` endpoints for topics, subtopics, patterns, vocabulary, daily phrase, and daily dialogue.
4. The router maps the UI into home, topics, conversations, patterns, vocabulary, and auth pages.

## Tech stack

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- FastAPI
- JSON content files

## Project structure

```text
frontend/
  src/
    components/      shared UI
    contexts/        auth and progress state
    pages/           home, topics, conversation, patterns, vocabulary
    lib/             API and data loading helpers
data-json/
  topics.json
  patterns.json
  vocabulary.json
  subtopics/         topic-specific lesson files
backend/
  api_content.py     content API routes
  main.py            API entry point
  vtutils/           config helpers
```

## Getting started

```bash
git clone <repo-url>
cd learn-swiss-german
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r pip/requirements.txt
cp .env.example .env
python main.py
```

Open:

- Frontend: `http://localhost:5306`
- API: `http://localhost:5206`
- API docs: `http://localhost:5206/docs`

## Configuration

Frontend:

```env
VITE_API_BASE=http://localhost:5206
```

Backend:

```env
VT_ENV=development
APP_PORT=5206
APP_HOST=0.0.0.0
PERMANENT_STORAGE=none
PERMANENT_DB=gruezi
```

## Usage

1. Start the frontend and backend locally.
2. Browse topics and open a subtopic or conversation.
3. Use the patterns and vocabulary sections for reference study.
4. Use the daily phrase and daily dialogue endpoints for rotating practice content.

To add a new subtopic, add a JSON file under `data-json/subtopics/` and update `data-json/subtopics/index.json`.

## Development

```bash
cd frontend && npm run dev
cd frontend && npm run build
cd frontend && npm run build:dev
cd frontend && npm run lint
cd frontend && npm run preview
cd backend && python main.py
```

There is currently no automated test suite in the repository.

## Roadmap

- Add more learning content and topic coverage
- Add automated tests for content loading and route behavior
- Add clearer learner progress features
- Document deployment for static frontend plus API hosting

## Contributing

This project is public and open for collaboration. If you’re interested in contributing, improving the project, or discussing ideas, feel free to reach out.

LinkedIn: https://linkedin.com/in/alexrada

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Open a pull request

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
