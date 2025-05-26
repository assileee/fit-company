from ..models_dto import UserSchema, UserResponseSchema, UserProfileSchema, UserProfileResponseSchema
from ..models_db import UserModel
from ..database import db_session
from typing import List, Optional
import random
import string
import hashlib

def generate_random_password(length=10):
    """Generate a random password of specified length"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(user: UserSchema) -> UserResponseSchema:
    """
    Create a new user with a random password and persist it to the database
    """
    # Generate a random password
    random_password = generate_random_password()
    hashed_password = hash_password(random_password)
    
    # Convert Pydantic model to SQLAlchemy model
    db_user = UserModel(
        email=user.email,
        name=user.name,
        role=user.role,
        password_hash=hashed_password
    )
    
    # Add and commit to database
    db = db_session()
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    
    # Return response including the clear-text password (one-time reveal)
    response = UserResponseSchema(
        email=user.email,
        name=user.name,
        role=user.role,
        password=random_password
    )
    
    return response

def get_all_users() -> List[UserSchema]:
    """
    Retrieve all users from the database
    """
    db = db_session()
    try:
        # Query all users from the database
        db_users = db.query(UserModel).all()
        
        # Convert SQLAlchemy models to Pydantic models
        return [
            UserSchema(
                email=db_user.email,
                name=db_user.name,
                role=db_user.role
            )
            for db_user in db_users
        ]
    finally:
        db.close()

def update_user_profile(email: str, profile: UserProfileSchema) -> Optional[UserProfileResponseSchema]:
    """
    Update user profile with weight, height, and fitness goal
    """
    db = db_session()
    try:
        # Find the user
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
            
        # Update the user's profile
        user.weight = profile.weight
        user.height = profile.height
        user.fitness_goal = profile.fitness_goal
        user.onboarded = "true"
        
        db.commit()
        db.refresh(user)
        
        # Return the updated user profile
        return UserProfileResponseSchema(
            email=user.email,
            name=user.name,
            weight=user.weight,
            height=user.height,
            fitness_goal=user.fitness_goal,
            onboarded=user.onboarded
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_user_profile(email: str) -> Optional[UserProfileResponseSchema]:
    """
    Get user profile information
    """
    db = db_session()
    try:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
            
        return UserProfileResponseSchema(
            email=user.email,
            name=user.name,
            weight=user.weight,
            height=user.height,
            fitness_goal=user.fitness_goal,
            onboarded=user.onboarded
        )
    finally:
        db.close()

from datetime import datetime, timedelta
from ..models_db import UserExerciseHistory, ExerciseModel, MuscleGroupModel, exercise_muscle_groups
from ..models_dto import Exercise, MuscleGroupWithPrimary
from ..database import db_session
import random

# Add these two functions in user_service.py

def add_exercise_history(user_email: str, exercise_id: int):
    """
    Add a record of the user completing an exercise at the current time.
    """
    db = db_session()
    try:
        history = UserExerciseHistory(
            user_email=user_email,
            exercise_id=exercise_id,
            date_done=datetime.utcnow()
        )
        db.add(history)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_recent_exercise_ids(user_email: str, within_hours: int = 24):
    """
    Get a set of exercise IDs done by the user within the last `within_hours` hours.
    """
    db = db_session()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=within_hours)
        records = db.query(UserExerciseHistory.exercise_id).filter(
            UserExerciseHistory.user_email == user_email,
            UserExerciseHistory.date_done >= cutoff
        ).all()
        return set(r[0] for r in records)
    finally:
        db.close()

def generate_wod_for_user(user_email: str, wod_size: int = 5):
    """
    Generate a WOD avoiding exercises done in the last 24 hours.
    Records the chosen exercises in history.
    Returns a list of Exercise DTOs.
    """
    db = db_session()
    try:
        recent_ids = get_recent_exercise_ids(user_email, within_hours=24)

        available_exercises = db.query(ExerciseModel).filter(
            ~ExerciseModel.id.in_(recent_ids)
        ).all()

        if not available_exercises:
            available_exercises = db.query(ExerciseModel).all()

        selected = random.sample(
            available_exercises,
            k=min(wod_size, len(available_exercises))
        )

        # Record exercises done now
        now = datetime.utcnow()
        for ex in selected:
            history = UserExerciseHistory(
                user_email=user_email,
                exercise_id=ex.id,
                date_done=now
            )
            db.add(history)
        db.commit()

        # Prepare DTOs with muscle groups
        result = []
        for exercise in selected:
            muscle_groups_data = db.query(
                MuscleGroupModel,
                exercise_muscle_groups.c.is_primary
            ).join(
                exercise_muscle_groups,
                MuscleGroupModel.id == exercise_muscle_groups.c.muscle_group_id
            ).filter(
                exercise_muscle_groups.c.exercise_id == exercise.id
            ).all()

            muscle_groups = [
                MuscleGroupWithPrimary.model_validate({
                    "id": mg[0].id,
                    "name": mg[0].name,
                    "body_part": mg[0].body_part,
                    "description": mg[0].description,
                    "is_primary": mg[1]
                }) for mg in muscle_groups_data
            ]

            exercise_dto = Exercise.model_validate({
                "id": exercise.id,
                "name": exercise.name,
                "description": exercise.description,
                "difficulty": exercise.difficulty,
                "equipment": exercise.equipment,
                "instructions": exercise.instructions,
                "muscle_groups": muscle_groups
            })
            result.append(exercise_dto)

        return result
    finally:
        db.close()