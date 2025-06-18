import logging
import os
from typing import List, Tuple

import requests
from .models_db import ExerciseModel, MuscleGroupModel, exercise_muscle_groups
from .database import db_session
import random
from time import time

logger = logging.getLogger(__name__)

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

def get_last_workout_exercises(user_email: str) -> List[int]:
    """
    Get the last workout exercises for a user from the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    history_response = requests.post(f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email})
    history_response.raise_for_status()
    return history_response.json()

def save_workout_exercises(user_email: str, exercise_ids: List[int]):
    """
    Save the workout exercises for a user to the monolith.
    """
    monolith_url = os.getenv("MONOLITH_URL")
    headers = {"X-API-Key": os.getenv("FIT_API_KEY")}
    requests.post(f"{monolith_url}/workouts/", headers=headers, json={"email": user_email, "exercises": exercise_ids})


def create_wod_for_user_service(user_email: str) -> List[Tuple[ExerciseModel, List[Tuple[MuscleGroupModel, bool]]]]:
    """
    Request a workout of the day (WOD).
    Returns a list of tuples containing:
    - The exercise
    - A list of tuples containing:
      - The muscle group
      - Whether it's a primary muscle group
    """

    logger.debug(f"running heavy computation to generate wod for user {user_email}")
    heavy_computation(random.randint(1, 5))  # DO NOT REMOVE
    logger.debug(f"heavy computation completed for user {user_email}")

    db = db_session()

    try:
        is_premium = is_user_premium(user_email)
        num_exercises = 9 if is_premium else 6

        last_exercise_ids = get_last_workout_exercises(user_email)

        available_exercises = db.query(ExerciseModel).filter(
            ~ExerciseModel.id.in_(last_exercise_ids)
        ).all()

        if len(available_exercises) < num_exercises:
            available_exercises = db.query(ExerciseModel).all()

        selected_exercises = random.sample(
            available_exercises, num_exercises
        ) if len(available_exercises) >= num_exercises else available_exercises

        save_workout_exercises(user_email, [exercise.id for exercise in selected_exercises])

        result = []
        for exercise in selected_exercises:
            stmt = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            )

            muscle_groups = [(mg, is_primary) for mg, is_primary in stmt.all()]
            result.append((exercise, muscle_groups))
        return result

    finally:
        db.close()

def is_user_premium(email: str) -> bool:
    fit_url = os.getenv("MONOLITH_URL", "http://monolith:5000")  # monolith
    resp = requests.get(f"{fit_url}/users/{email}/goal")
    if resp.status_code == 200:
        return resp.json().get("fitness_goal") == "premium"
    return False
