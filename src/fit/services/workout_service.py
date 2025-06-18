from datetime import datetime
from typing import List, Dict, Optional

import requests
from ..database import db_session
from ..models_db import UserExerciseHistory, WorkoutModel
from ..models_dto import ExerciseId, WodExerciseSchema, WorkoutExercisesList, WorkoutResponseSchema, ExercisePerformanceSchema
from sqlalchemy import func
from .rabbitmq_service import rabbitmq_service

import os

def register_workout(user_email: str, exercise_data: List[ExercisePerformanceSchema]):
    db = db_session()
    try:
        workout = WorkoutModel(
            user_email=user_email,
            created_at=datetime.utcnow(),
            performed_at=None
        )
        db.add(workout)
        db.flush()

        for ex in exercise_data:
            entry = UserExerciseHistory(
                workout_id=workout.id,
                exercise_id=ex.exercise_id,
                reps=ex.reps,
                weight=ex.weight
            )
            db.add(entry)

        db.commit()

    finally:
        db.close()

def get_exercises_metadata(exercise_ids: List[int]) -> List[WodExerciseSchema]:
    """
    Get the metadata for a list of exercise IDs.
    """
    coach_url = os.getenv("COACH_URL")
    history_response = requests.get(f"{coach_url}/exercises")
    history_response.raise_for_status()
    history_exercises = history_response.json()

    filtered_exercises = []
    for exercise in history_exercises:
        if exercise['id'] in exercise_ids:
            filtered_exercises.append(exercise)
    return filtered_exercises


def get_user_next_workout(user_email: str) -> Optional[WorkoutResponseSchema]:
    """
    Get the next workout for a user.
    """
    workout = get_most_recent_workout_exercises(user_email, performed=False)
    if workout is None:
        return None
    exercises_populated = get_exercises_metadata(workout.exercises)
    return WorkoutResponseSchema(
        id=workout.workout_id,
        exercises=exercises_populated
    )

def get_most_recent_workout_exercises(user_email: str, performed: bool) -> Optional[WorkoutExercisesList]:
    """
    Get the exercises from the user's most recent workout based on its performed status.
    
    Args:
        user_email (str): The email of the user
        performed (bool): If True, returns the last performed workout. If False, returns the last unperformed workout.
    
    Returns:
        Optional[WorkoutResponseSchema]: Workout ID and list of exercise IDs or None if no matching workout exists.
    """
    db = db_session()
    try:
        # Build the query based on performed status
        query = db.query(WorkoutModel).filter(
            WorkoutModel.user_email == user_email
        )
        
        if performed:
            query = query.filter(WorkoutModel.performed_at.isnot(None))
            query = query.order_by(WorkoutModel.performed_at.desc())
        else:
            query = query.filter(WorkoutModel.performed_at.is_(None))
            query = query.order_by(WorkoutModel.created_at.desc())
            
        last_workout = query.first()
        
        if not last_workout:
            return None
            
        # Get exercises from the last workout
        exercises = db.query(
            UserExerciseHistory
        ).filter(
            UserExerciseHistory.workout_id == last_workout.id
        ).all()
        
        exercise_ids = []
        for exercise in exercises:
            exercise_ids.append(exercise.exercise_id)
            
        return WorkoutExercisesList(
            workout_id=last_workout.id,
            exercises=exercise_ids
        )
    finally:
        db.close()

def perform_workout(workout_id: int, user_email: str):
    """
    Mark a workout as performed by setting its performed_at timestamp.
    Also publishes a workout.performed event.
    """
    db = db_session()
    try:
        workout = db.query(WorkoutModel).filter(
            WorkoutModel.id == workout_id
        ).first()
        
        if workout and workout.user_email == user_email:
            workout.performed_at = datetime.utcnow()

            # Get number of exercises in this workout
            exercise_count = db.query(UserExerciseHistory).filter_by(workout_id=workout_id).count()

            # Prepare workout event payload
            event = {
                "user_email": workout.user_email,
                "workout_date": workout.performed_at.isoformat(),
                "duration_min": 40,            # placeholder, replace with actual logic if needed
                "calories_burned": 500,        # placeholder
                "exercises_completed": exercise_count
            }

            # Publish workout.performed event
            rabbitmq_service.publish_workout_performed_event(event)

            db.commit()
        else:
            raise Exception("Workout not found or user does not have access to this workout")
    finally:
        db.close()
