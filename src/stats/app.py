from flask import Flask, jsonify
from database import db_session, init_db
from models import WorkoutStat

app = Flask(__name__)
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/stats', methods=['GET'])
def get_all_stats():
    stats = db_session.query(WorkoutStat).all()
    return jsonify([
        {
            "email": stat.user_email,
            "date": stat.workout_date,
            "duration": stat.duration_min,
            "calories": stat.calories_burned,
            "exercises": stat.exercises_completed
        } for stat in stats
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
