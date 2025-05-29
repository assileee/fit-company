from typing import List, Tuple
from ..models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups, UserExerciseHistory
from ..database import db_session
import random
from time import time
from datetime import datetime, timezone

def heavy_computation(duration_seconds: int = 3):
    """
    Perform CPU-intensive calculations to simulate heavy processing.
    Uses matrix operations which are CPU-intensive.
    """
    start_time = time()
    i = 0
    while (time() - start_time) < duration_seconds:
        j = 0
        while j < 1000000:
            j += 1
        i += 1

def calculate_intensity(difficulty: int) -> float:
    """
    Calculate the intensity of an exercise based on its difficulty level (1-5).
    Returns a value between 0.0 and 1.0.
    """
    # Convert difficulty (1-5) to intensity (0.0-1.0)
    return (difficulty - 1) / 4.0

def request_wod(user_email: str):
    db = db_session()
    try:
        # Get today's date (UTC)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Get exercise IDs the user has already done today
        recent_ex_ids = db.query(UserExerciseHistory.exercise_id)\
            .filter(UserExerciseHistory.user_email == user_email)\
            .filter(UserExerciseHistory.date_performed >= today_start)\
            .all()
        excluded_ids = [row.exercise_id for row in recent_ex_ids]

        # Get all exercises excluding today's
        exercises = db.query(ExerciseModel).filter(~ExerciseModel.id.in_(excluded_ids)).all()
        if not exercises:
            exercises = db.query(ExerciseModel).all()

        selected = random.sample(exercises, min(len(exercises), 6))

        result = []

        for exercise in selected:
            # Load muscle group data while session is still open
            muscle_groups_query = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            ).all()

            muscle_groups = [(mg, is_primary) for mg, is_primary in muscle_groups_query]
            result.append((
                {
                    "id": exercise.id,
                    "name": exercise.name,
                    "description": exercise.description,
                    "difficulty": exercise.difficulty,
                    "equipment": exercise.equipment,
                    "instructions": exercise.instructions
                },
                [
                    {
                        "id": mg.id,
                        "name": mg.name,
                        "body_part": mg.body_part,
                        "is_primary": is_primary
                    }
                    for mg, is_primary in muscle_groups
                ]
            ))

            # Save this exercise in user's history
            db.add(UserExerciseHistory(
                user_email=user_email,
                exercise_id=exercise.id,
                date_performed=datetime.now(timezone.utc)
            ))

        db.commit()
        return result

    finally:
        db.close()