# coach/wod_consumer.py

import pika
import os
import json
from coach.fitness_coach_service import save_wod_for_user

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        user_email = message.get("user_email")
        exercise_ids = message.get("exercise_ids", [])

        print(f"[COACH] Creating WOD for {user_email}")
        save_wod_for_user(user_email, exercise_ids)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[ERROR] {e}")
        
        # If message has been redelivered, send to DLQ
        if method.redelivered:
            print(f"[DLQ] Moving message to DLQ: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.basic_publish(
                exchange='',
                routing_key='dlqQueue',
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )
        else:
            # Requeue the message to retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
        os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=5672,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue="createWodQueue", durable=True)
    channel.queue_declare(queue="dlqQueue", durable=True)

    channel.basic_consume(
        queue="createWodQueue",
        on_message_callback=callback
    )

    print("[*] Waiting for WOD jobs...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
