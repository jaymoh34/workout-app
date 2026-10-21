from datetime import date

from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Bool(load_default=False)

    @validates("name")
    def validate_name_not_blank(self, value):
        if not value.strip():
            raise ValidationError("Name cannot be blank.")

    @validates("category")
    def validate_category_not_blank(self, value):
        if not value.strip():
            raise ValidationError("Category cannot be blank.")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=validate.Range(min=1, max=600))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))

    @validates("date")
    def validate_date(self, value):
        if value < date(2000, 1, 1):
            raise ValidationError("Date must be on or after 2000-01-01.")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(load_default=None, allow_none=True, strict=True, validate=validate.Range(min=1))
    sets = fields.Int(load_default=None, allow_none=True, strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(
        load_default=None, allow_none=True, strict=True, validate=validate.Range(min=1)
    )
    # Related objects are serialized only; nested copies exclude the back-reference
    # to avoid infinite recursion.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError("Provide reps or duration_seconds.", "reps")
        if data.get("sets") is not None and data.get("reps") is None:
            raise ValidationError("sets requires reps.", "sets")


class WorkoutDetailSchema(WorkoutSchema):
    """Workout plus its exercises, including reps/sets/duration."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema(exclude=("workout",)), many=True, dump_only=True
    )


class ExerciseDetailSchema(ExerciseSchema):
    """Exercise plus the workouts it appears in."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema(exclude=("exercise",)), many=True, dump_only=True
    )
