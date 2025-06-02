import requests
import random
from typing import List
import os

MONOLITH_URL = os.getenv("MONOLITH_URL", "http://api:5000")  # Docker service name

def generate_wod(user_email: str, excluded_ids: List[int]):
    try:
        # Step 1: Get all exercises from monolith
        response = requests.get(f"{MONOLITH_URL}/fitness/exercises")
        if response.status_code != 200:
            raise Exception("Failed to fetch exercises from monolith")
        
        all_exercises = response.json()
        if not isinstance(all_exercises, list):
            raise Exception("Invalid response format from /fitness/exercises")

        # Step 2: Exclude exercises already done today
        filtered_exercises = [ex for ex in all_exercises if ex["id"] not in excluded_ids]

        # If all were excluded, fallback to all
        if not filtered_exercises:
            filtered_exercises = all_exercises

        # Step 3: Randomly pick up to 6
        selected = random.sample(filtered_exercises, min(len(filtered_exercises), 6))

        return selected

    except Exception as e:
        print(f"[ERROR in coach_service] {e}")
        raise e
