# Workout Tracker API

## Description
A Flask REST API for personal trainers to track workouts and the exercises in them. Exercises are reusable across workouts, and each workout–exercise link stores sets, reps and/or duration. Built with Flask, SQLAlchemy, Flask-Migrate and Marshmallow (SQLite database).

**Data model:** `Workout` ⟷ `WorkoutExercise` ⟷ `Exercise` (many-to-many through the join table).

**Validation layers**
- **Table constraints:** unique exercise name, non-blank name/category, workout duration between 1 and 600, positive reps/sets/duration, reps or duration required, one row per workout/exercise pair.
- **Model validations:** non-blank text, boolean `equipment_needed`, valid date, positive integers for duration/reps/sets.
- **Schema validations:** length/range checks, blank-string checks, date lower bound, "reps or duration_seconds required", "sets requires reps".

## Installation
```bash
git clone <your-repo-url>
cd <repo>
pipenv install
pipenv shell
cd server
flask db upgrade head      # migrations are already included
python seed.py             # resets and loads example data
```
If you prefer to regenerate migrations: delete `server/migrations`, then run `flask db init`, `flask db migrate -m "message"`, `flask db upgrade head`.

## Run
```bash
cd server
export FLASK_APP=app.py
flask run -p 5555
```
or `python app.py`. The API is served at `http://localhost:5555`.

## Tests
```bash
cd server
pipenv install --dev
pytest
```

## Endpoints
| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/<id>` | One workout with its exercises, including reps/sets/duration | 200 |
| POST | `/workouts` | Create a workout: `{"date": "2026-10-19", "duration_minutes": 45, "notes": "optional"}` | 201 |
| DELETE | `/workouts/<id>` | Delete a workout and its workout-exercises | 204 |
| GET | `/exercises` | List all exercises | 200 |
| GET | `/exercises/<id>` | One exercise with the workouts it appears in | 200 |
| POST | `/exercises` | Create an exercise: `{"name": "Plank", "category": "Core", "equipment_needed": false}` | 201 |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout-exercises | 204 |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout: `{"sets": 3, "reps": 10}` or `{"duration_seconds": 60}` | 201 |

**Errors** (JSON `{"errors": ...}`): `400` validation failure, `404` not found, `409` constraint conflict (e.g. duplicate exercise name, exercise already in workout).
