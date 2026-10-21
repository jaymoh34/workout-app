#!/usr/bin/env python3
from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    # Clear in child-to-parent order so reruns never duplicate data.
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    squat = Exercise(name="Barbell Squat", category="Strength", equipment_needed=True)
    pushup = Exercise(name="Push-up", category="Strength", equipment_needed=False)
    plank = Exercise(name="Plank", category="Core", equipment_needed=False)
    run = Exercise(name="Treadmill Run", category="Cardio", equipment_needed=True)
    db.session.add_all([squat, pushup, plank, run])

    print("Seeding workouts...")
    leg_day = Workout(date=date(2026, 10, 12), duration_minutes=60, notes="Heavy leg day")
    full_body = Workout(date=date(2026, 10, 14), duration_minutes=45, notes="Bodyweight circuit")
    cardio = Workout(date=date(2026, 10, 16), duration_minutes=30, notes=None)
    db.session.add_all([leg_day, full_body, cardio])
    db.session.commit()

    print("Seeding workout exercises...")
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, sets=4, reps=8),
        WorkoutExercise(workout=leg_day, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=full_body, exercise=pushup, sets=3, reps=15),
        WorkoutExercise(workout=full_body, exercise=plank, sets=3, duration_seconds=45),
        WorkoutExercise(workout=cardio, exercise=run, duration_seconds=1500),
    ])
    db.session.commit()
    print("Done seeding!")
