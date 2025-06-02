## Estimate load:

   For Loadtest.js, these were the settings:

    { duration: '30s', target: 10 }, // Ramp-up to 10 VUs in 30s
    { duration: '30s', target: 15 }, // Hold at 15 VUs for 30s
    { duration: '30s', target: 50 }, // Ramp-up to 50 VUs over 30s
    { duration: '30s', target: 75 }, // Ramp-up to 75 VUs over 30s
    { duration: '30s', target: 100 }, // Ramp-up to 100 VUs over 30s
    { duration: '1m', target: 100 }, // Hold at 100 VUs for 1 minute
    { duration: '30s', target: 50 }, // Ramp-down to 50 VUs in 30 seconds
    { duration: '30s', target: 10 },  // Ramp-down to 10 VUs in 30s
    { duration: '1m', target: 0 },  // Ramp-down to 0 VUs in 1 minute (graceful stop)


The total results were :
- 69% had a response time of <5s

Based on the req_duration:
- the average is just above the target : avg=5.79s
- the median shows that approximately 1-30 virtual users were pretty fast :med=1.71s 

But since p(90)=17.62s, from approximatly 40 to 50 Vus the response starts to aggravate.
Finally, p(95)=29.53s, so around 60 the system is too overloaded !!

In conclusion, with the help of k6 we found that we can scale up to 30 VUs with our current infrastrucutre.

## First microservice "Coach"

1. Two services in docker-compose.yml : monolith + coach service 

We made sure to make "coach" a seperate service with its own Dockerfile

- api running flask (src/fit/app.py)
- coach running coach/main.py

2. Coach service exposes API to generate WODs

For this we exposed POST /api/coach/WOD in coach/main.py but the actual function to generate the WOD is in coach_service.py

3. Coach service should request monolith to get yesterday's user's exercices history

We included a blocking HTTP request in coach_service.py

 "response = requests.get(f"{MONOLITH_URL}/fitness/exercises")"

This url points us to the MONOLITH, so it fetches all exercices from there using Docker.
To exclude exercices already done today we added "excluded_ids" in the POST body.

4. They should communicate through synchronous blocking
To be able to have real time communication between the services we used synchronous blocking.

Inside coach/coach_service.py we used "requests.get()", like we mentioned in the step earlier, its a blocking HTTP request (synchronous) from the "coach" service to the monolith api service.

The "requests.get()" waits for a response from the monolith, and blocks it till there is a response or timeout.

5. All Used APIs should be documented using OpenAPI spec

Please see coach/openapi.yaml to view API documentation using OpenAPI 3.0.

6. Migration guide using a strangler fig pattern

Before applying Strangler Fig Pattern , the Monolith was doing everything. So we created coach/coach_service.py to pull exercices from the monolith.
Afterwards, we exposed the /api/coach/WOD in coach/main.py so that the logic can be via the new coach service.
We allowed coach to communicate with the Monolith using Docker DNS (docker-compose.yml).

Using this method we can allow "coach" to be independent without messing with the Monolith, the API is fully tested.
This also allowed us to gradually migrate, and not mess up the project.
