# Gym Tracker API

A simple REST API for logging strength-training workouts, built with Flask and SQLAlchemy.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

The server runs at `http://localhost:5000`. A SQLite database file (`gym_tracker.db`) is created automatically on first run.

## Endpoints

### Log a new session
`POST /sessions`

```json
{
  "date": "2026-09-09",
  "exercises": [
    {"exercise_name": "Bench Press", "set_number": 1, "reps": 8, "weight": 60},
    {"exercise_name": "Bench Press", "set_number": 2, "reps": 8, "weight": 60}
  ]
}
```

### View full history
`GET /sessions`

### View one session
`GET /sessions/<id>`

### Delete a session
`DELETE /sessions/<id>`

### Quick reference: last time you did an exercise
`GET /exercises/<name>/last`

### All-time PR for an exercise
`GET /exercises/<name>/pr`

### Suggested target for next session
`GET /exercises/<name>/suggestion`

Uses simple progressive-overload logic: if every set in your last session for that exercise hit 8+ reps, it suggests a small weight increase; otherwise it suggests repeating the same weight.

## Project structure

- `models.py` — database models (`Session`, `SetEntry`) and their relationship
- `app.py` — Flask routes (the API itself)

## Possible next steps

- Add a simple frontend (HTML form + JS) to log sessions without using an API client
- Replace the rule-based suggestion with a call to an LLM API for more nuanced, explained suggestions
- Add authentication if this were ever used by more than one person
