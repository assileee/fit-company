import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.fit import User  # adjust if your User model is elsewhere

# Setup DB connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Coach service URL
COACH_URL = os.getenv("COACH_URL", "http://coach:5000/createWod")
API_KEY = os.getenv("FIT_API_KEY")

def trigger_wod_creation():
    session = Session()
    try:
        users = session.query(User).all()
        for user in users:
            response = requests.post(
                COACH_URL,
                headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                json={"user_email": user.email}
            )
            print(f"[WOD] {user.email}: {response.status_code} - {response.text}")
    finally:
        session.close()

if __name__ == "__main__":
    trigger_wod_creation()
