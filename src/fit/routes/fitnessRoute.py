from flask import Blueprint, request, jsonify, g
from ..services.fitness_service import get_all_exercises, get_exercise_by_id, get_exercises_by_muscle_group
from ..services.fitness_coach_service import calculate_intensity, request_wod
from ..models_dto import WodResponseSchema, WodExerciseSchema, MuscleGroupImpact
from ..services.auth_service import jwt_required
import datetime
import random

fitness_bp = Blueprint("fitness", __name__)

@fitness_bp.route("/fitness/exercises", methods=["GET"])
def get_exercises():
    try:
        muscle_group_id = request.args.get("muscle_group_id")
        if muscle_group_id:
            exercises = get_exercises_by_muscle_group(int(muscle_group_id))
        else:
            exercises = get_all_exercises()
        return jsonify([ex.model_dump() for ex in exercises]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercises", "details": str(e)}), 500

@fitness_bp.route("/fitness/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    try:
        exercise = get_exercise_by_id(exercise_id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise.model_dump()), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving exercise", "details": str(e)}), 500

@fitness_bp.route("/fitness/wod", methods=["GET"])
@jwt_required
def get_wod():
    try:
        exercises_with_muscles = request_wod()
        wod_exercises = []
        for exercise, muscle_groups in exercises_with_muscles:
            muscle_impacts = [
                MuscleGroupImpact(
                    id=mg.id,
                    name=mg.name,
                    body_part=mg.body_part,
                    is_primary=is_primary,
                    intensity=calculate_intensity(exercise.difficulty) * (1.2 if is_primary else 0.8)
                )
                for mg, is_primary in muscle_groups
            ]

            wod_exercise = WodExerciseSchema(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                difficulty=exercise.difficulty,
                muscle_groups=muscle_impacts,
                suggested_weight=random.uniform(5.0, 50.0),
                suggested_reps=random.randint(8, 15)
            )
            wod_exercises.append(wod_exercise)

        response = WodResponseSchema(
            exercises=wod_exercises,
            generated_at=datetime.datetime.now(datetime.UTC).isoformat()
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({"error": "Error generating workout of the day", "details": str(e)}), 500