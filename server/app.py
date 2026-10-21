import os
import sqlite3

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    ExerciseDetailSchema,
    ExerciseSchema,
    WorkoutDetailSchema,
    WorkoutExerciseSchema,
    WorkoutSchema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()
workout_exercise_schema = WorkoutExerciseSchema()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _):
    """SQLite ignores foreign keys unless this pragma is set per connection."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ---------- Error handlers ----------

@app.errorhandler(ValidationError)
def handle_schema_error(err):
    return jsonify({"errors": err.messages}), 400


@app.errorhandler(ValueError)
def handle_model_validation_error(err):
    return jsonify({"errors": [str(err)]}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    db.session.rollback()
    return jsonify({"errors": ["Database constraint violated (e.g. duplicate or invalid value)."]}), 409


@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({"errors": ["Resource not found."]}), 404


def json_body():
    """Return the JSON payload, or raise a 400-style error if missing/invalid."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError({"_schema": ["Request body must be a JSON object."]})
    return data


# ---------- Workouts ----------

@app.route("/workouts", methods=["GET"])
def get_workouts():
    return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.date).all())), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = db.get_or_404(Workout, id)
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = workout_schema.load(json_body())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = db.get_or_404(Workout, id)
    db.session.delete(workout)  # cascades to WorkoutExercises
    db.session.commit()
    return "", 204


# ---------- Exercises ----------

@app.route("/exercises", methods=["GET"])
def get_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.name).all())), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = db.get_or_404(Exercise, id)
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = exercise_schema.load(json_body())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = db.get_or_404(Exercise, id)
    db.session.delete(exercise)  # cascades to WorkoutExercises
    db.session.commit()
    return "", 204


# ---------- Workout exercises ----------

@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.get_or_404(Workout, workout_id)
    exercise = db.get_or_404(Exercise, exercise_id)
    data = workout_exercise_schema.load(json_body())
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
