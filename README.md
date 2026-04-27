# ScribeUp Take-Home — Subscription Detection

Welcome! This is the starter repo for the ScribeUp coding challenge.

The take-home is intentionally under-specified — closer to how a real ticket lands at a small startup than a clean spec. We care more about your judgment than completeness; don't polish. Plan on roughly **3 hours** of your own time.

## What's here

- `backend/` — Django + SQLite project with a `Transaction` model and a seed script that generates realistic subscription data.
- `frontend/` — A minimal Vite + React app that lists transactions for a user.

The seed script generates ~5,000 fake transactions across ~50 users — a mix of real recurring subscriptions, near-recurring noise, and one-off purchases. SQLite is used so there's nothing to install beyond Python and Node.

## Running locally

You'll need: Python 3.11+ and Node 20+.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed   # generates ~5,000 transactions across ~50 users
python manage.py runserver

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:5173`.

## What's already wired up

- `GET /users/` — returns the list of seeded user IDs.
- `GET /users/<user_id>/transactions/` — returns all transactions for a user. The React page calls this.
- The React page has a user selector and a simple transaction list.

## The prompt

Build a `GET /users/<user_id>/subscriptions/` endpoint that returns the recurring subscriptions detected for that user. For each subscription, return at minimum:

- merchant
- cadence (monthly / weekly / yearly / unknown)
- typical amount
- next predicted charge date

Then wire it up to the React page so a user can see their detected subscriptions alongside their transactions.

## AI policy

Use any AI tools you'd normally use — Cursor, Copilot, Claude, ChatGPT, all fair game. We assume you will. We'll want to see how well you understand what you (and your AI) shipped, so use AI as a force multiplier, not a crutch.

## Tips

- Look at the seeded data before you start coding — there are interesting edge cases worth noticing.
- The schema is intentionally minimal — if you want to add fields or tables, that's a design decision worth defending.
- Don't polish — we'd rather see honest trade-offs than perfect code.
- If something is genuinely unclear, ask

## What to submit

A zip file with your changes, plus a `NOTES.md` at the root covering:

1. What you'd do differently with more time.
2. Where you used AI tools and where you didn't.
3. Trade-offs you made and why.

Questions? Please reach out
# scribeup-coding-challenge-2026
