import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 2 }, 
    { duration: '4m', target: 2 },  
    { duration: '30s', target: 0 },  
  ],
};

export default function () {
  const res = http.get('http://localhost:5001/fitness/wod', {
  headers: {
    Authorization: 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqYW5lLmRvZUBtYWlsLmNvbSIsIm5hbWUiOiJKYW5lIERvZSIsInJvbGUiOiJhZG1pbiIsImlzcyI6ImZpdC1hcGkiLCJpYXQiOjE3NDg0NjU0MjUsImV4cCI6MTc0ODQ2OTAyNX0.Jltz_TNZgojDUJwMyPx6yySCarF0AzDrJJoGU_Bd_BY'
  },
});

// console.log(`Response time: ${res.timings.duration} ms`);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });

  sleep(1);
}

