from sqlalchemy import Column, Integer, String, Float
from database import Base

class WorkoutStat(Base):
    __tablename__ = 'workout_stats'

    id = Column(Integer, primary_key=True)
    user_email = Column(String, nullable=False)
    workout_date = Column(String, nullable=False)
    duration_min = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    exercises_completed = Column(Integer, nullable=False)
