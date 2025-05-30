import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp-up to 10 VUs in 30s
    { duration: '30s', target: 15 }, // Hold at 15 VUs for 30s
    { duration: '30s', target: 50 }, // Ramp-up to 50 VUs over 30s
    { duration: '30s', target: 75 }, // Ramp-up to 75 VUs over 30s
    { duration: '30s', target: 100 }, // Ramp-up to 100 VUs over 30s
    { duration: '1m', target: 100 }, // Hold at 100 VUs for 1 minute
    { duration: '30s', target: 50 }, // Ramp-down to 50 VUs in 30 seconds
    { duration: '30s', target: 10 },  // Ramp-down to 10 VUs in 30s
    { duration: '1m', target: 0 },  // Ramp-down to 0 VUs in 1 minute (graceful stop)


  ],
};

export default function () {
  const res = http.get('http://localhost:5001/fitness/wod', {
  headers: {
    Authorization: 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqYW5lLmRvZUBtYWlsLmNvbSIsIm5hbWUiOiJqYW5lIGRvZSIsInJvbGUiOiJhZG1pbiIsImlzcyI6ImZpdC1hcGkiLCJpYXQiOjE3NDg2MDg4MTEsImV4cCI6MTc0ODYxMDYxMX0.0Gco-dSPtqWMuwtP-Z33VZrQoSl43AXVEX4bttiqyZo'
  },
});

// console.log(`Response time: ${res.timings.duration} ms`);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });

  sleep(1);
}

