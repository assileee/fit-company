from flask import Flask, jsonify
from database import db_session, init_db
from models import WorkoutStat
from threading import Thread
from wod_consumer import main as run_consumer  # import your RabbitMQ consumer

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

def start_consumer():
    """Start the RabbitMQ consumer in a background thread"""
    thread = Thread(target=run_consumer, daemon=True)
    thread.start()

if __name__ == "__main__":
    print("caelled main")
    start_consumer()
    app.run(host="0.0.0.0", port=5002)
