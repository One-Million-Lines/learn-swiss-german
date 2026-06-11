# Contributing

Thanks for your interest in contributing.

## Local setup

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

## Making changes

- Keep new lesson content in `data-json/`
- Update `data-json/subtopics/index.json` when adding new subtopic files
- Run `frontend` build and lint commands before opening a pull request

## Pull requests

1. Fork the repository
2. Create a branch for your change
3. Make your changes
4. Open a pull request with context and screenshots where useful

## Reporting issues

Open a GitHub issue with reproduction steps, the affected topic or subtopic, and any API errors.
