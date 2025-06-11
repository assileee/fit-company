### Create queue programatically

- To meet the queue requirements the messages were set to stay for 1min instead of 10mins.

### Create producer in the monolith

- Firstly, we created  wod_blueprint.py, and included an API route that defines a POST endpoint

@wod_bp.route("/generate", methods=["POST"])
def generate_wods_for_all_users():

That way wehn its triggered it creates WODs for all users.

- Second to fetch all users we added this :

users = get_all_users()

- Next, to create one message per user to the createWodQueue:

for user in users:
    message = {
        "user_email": user.email,
        "exercise_ids": []
    }
    rabbitmq_service.publish_message(message)

This creates a simple message for each user and publishes it via rabbitmq_service.

And at the end we returned the number of queued messages.

### Create consumer in the coach service

- We created wod_consumer.py, 

createWodQueue: is where WOD creation jobs are sent
dlqQueue: where failed jobs are sent after failed attempsts

- Messages are sent to the callback() function which hadnles WOD creations whihc calls save_wod_for_user(...) to save the WOD in the coach db.

- For the API we added /wod endpoint in coach/app.py

@app.route("/wod", methods=["GET"])
def get_user_wod():

### Validate the system

- First off we modified request_wod.py in fitness_coach_service.py to randomly fail

import random
FAILURE_PROBABILITY = float(os.getenv("WOD_FAILURE_RATE", "0.2"))

if random.random() < FAILURE_PROBABILITY:
    raise RuntimeError("Simulated WOD generation failure")

### Create a cron job in the monolith

- We queried all users, same logic as /generate route.
- Then we called the coach API for each user

response = requests.post(
    COACH_URL,
    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
    json={"user_email": user.email}
)

For each user the script makes a POST request tp /createWod on the coach service and triggers requewst_wod() logic inside the coach app.


