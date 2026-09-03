import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  duration: '30s',
};

export default function () {
  const url = `${__ENV.BASE_URL}/create-post`;

  const payload = JSON.stringify({
    title: 'Performance Test',
    content: 'This is a performance test',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(url, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}