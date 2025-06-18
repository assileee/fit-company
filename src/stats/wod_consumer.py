import os
import pika
import json
from database import db_session, init_db
from models import WorkoutStat

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
EXCHANGE_NAME = "workout.performed"

def store_stat(event):
    session = db_session()
    try:
        stat = WorkoutStat(
            user_email=event["user_email"],
            workout_date=event["workout_date"],
            duration_min=event["duration_min"],
            calories_burned=event["calories_burned"],
            exercises_completed=event["exercises_completed"]
        )
        session.add(stat)
        session.commit()
        print(f"[✓] Stored workout stat for {event['user_email']}")
    except Exception as e:
        session.rollback()
        print("[x] Error storing stat:", e)
    finally:
        session.close()

def callback(ch, method, properties, body):
    try:
        event = json.loads(body)
        store_stat(event)
    except Exception as e:
        print("[x] Failed to process message:", e)

def main():
    init_db()

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    # Declare exchange and temporary queue
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

    print('[*] Waiting for workout.performed messages. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
