from ..database import db_session
from ..models_db import MuscleGroupModel, ExerciseModel, exercise_muscle_groups
from ..models_dto import MuscleGroup, Exercise, MuscleGroupWithPrimary
from sqlalchemy import select, join

def get_all_muscle_groups():
    db = db_session()
    try:
        muscle_groups = db.query(MuscleGroupModel).all()
        return [MuscleGroup(
            id=mg.id,
            name=mg.name,
            body_part=mg.body_part,
            description=mg.description
        ) for mg in muscle_groups]
    finally:
        db.close()

def get_muscle_group_by_id(muscle_group_id: int):
    db = db_session()
    try:
        muscle_group = db.query(MuscleGroupModel).filter(MuscleGroupModel.id == muscle_group_id).first()
        if not muscle_group:
            return None
        
        return MuscleGroup(
            id=muscle_group.id,
            name=muscle_group.name,
            body_part=muscle_group.body_part,
            description=muscle_group.description
        )
    finally:
        db.close()

def get_all_exercises():
    db = db_session()
    try:
        exercises = db.query(ExerciseModel).all()
        
        result = []
        for exercise in exercises:
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
                MuscleGroupWithPrimary(
                    id=mg[0].id,
                    name=mg[0].name,
                    body_part=mg[0].body_part,
                    description=mg[0].description,
                    is_primary=mg[1]
                ) for mg in muscle_groups_data
            ]
            
            exercise_dto = Exercise(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                equipment=exercise.equipment,
                instructions=exercise.instructions,
                muscle_groups=muscle_groups
            )
            
            result.append(exercise_dto)
            
        return result
    finally:
        db.close()

def get_exercise_by_id(exercise_id: int):
    db = db_session()
    try:
        exercise = db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id).first()
        if not exercise:
            return None
        
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
            MuscleGroupWithPrimary(
                id=mg[0].id,
                name=mg[0].name,
                body_part=mg[0].body_part,
                description=mg[0].description,
                is_primary=mg[1]
            ) for mg in muscle_groups_data
        ]
        
        return Exercise(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            difficulty=exercise.difficulty,
            equipment=exercise.equipment,
            instructions=exercise.instructions,
            muscle_groups=muscle_groups
        )
    finally:
        db.close()

def get_exercises_by_muscle_group(muscle_group_id: int):
    db = db_session()
    try:
        exercises = db.query(ExerciseModel).join(
            exercise_muscle_groups,
            ExerciseModel.id == exercise_muscle_groups.c.exercise_id
        ).filter(
            exercise_muscle_groups.c.muscle_group_id == muscle_group_id
        ).all()
        
        result = []
        for exercise in exercises:
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
                MuscleGroupWithPrimary(
                    id=mg[0].id,
                    name=mg[0].name,
                    body_part=mg[0].body_part,
                    description=mg[0].description,
                    is_primary=mg[1]
                ) for mg in muscle_groups_data
            ]
            
            exercise_dto = Exercise(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                equipment=exercise.equipment,
                instructions=exercise.instructions,
                muscle_groups=muscle_groups
            )
            
            result.append(exercise_dto)
            
        return result
    finally:
        db.close()
