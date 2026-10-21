from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db


def test_exercise_name_cannot_be_blank(client):
    with pytest.raises(ValueError):
        Exercise(name="  ", category="Core")


def test_workout_duration_must_be_positive(client):
    with pytest.raises(ValueError):
        Workout(date=date.today(), duration_minutes=0)


def test_workout_exercise_reps_must_be_positive(client):
    with pytest.raises(ValueError):
        WorkoutExercise(reps=-3)


def test_exercise_name_unique_constraint(client):
    db.session.add_all([Exercise(name="Plank", category="Core"), Exercise(name="Plank", category="Core")])
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_workout_exercise_needs_reps_or_duration(client):
    w = Workout(date=date.today(), duration_minutes=30)
    e = Exercise(name="Row", category="Strength")
    db.session.add(WorkoutExercise(workout=w, exercise=e))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_relationships(client):
    w = Workout(date=date.today(), duration_minutes=30)
    e = Exercise(name="Row", category="Strength")
    db.session.add(WorkoutExercise(workout=w, exercise=e, reps=10, sets=3))
    db.session.commit()
    assert w.exercises == [e]
    assert e.workouts == [w]
