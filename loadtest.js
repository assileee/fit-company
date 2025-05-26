import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 }, 
    { duration: '1m', target: 10 },  
    { duration: '30s', target: 0 },  
  ],
};

export default function () {
  const res = http.get('http://localhost:8000/fitness/wod');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });

  sleep(1);
}

