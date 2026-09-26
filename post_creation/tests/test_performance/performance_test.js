import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 25 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 75 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 150 },
    { duration: '30s', target: 200 },
    { duration: '30s', target: 0 },
  ],

  
  thresholds: {
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.POST_CREATION_DEPLOYED_URL;
const SUPABASE_URL = __ENV.SUPABASE_PROJECT_URL;
const SUPABASE_KEY = __ENV.SUPABASE_PUBLISHABLE_KEY;
const TEST_USER_EMAIL = __ENV.TEST_USER_EMAIL;
const TEST_USER_PASSWORD = __ENV.TEST_USER_PASSWORD;


// --------------------------------------------------
// Setup
// --------------------------------------------------

export function setup() {

  // Authenticate once before the test starts
  const response = http.post(
    `${SUPABASE_URL}/auth/v1/token?grant_type=password`,
    JSON.stringify({
      email: TEST_USER_EMAIL,
      password: TEST_USER_PASSWORD,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
      },
    }
  );

  check(response, {
    'Supabase login successful': (r) => r.status === 200,
  });

  if (response.status !== 200) {
    throw new Error(`Supabase login failed: ${response.status}`);
  }

  return {
    accessToken: response.json('access_token'),
  };
}


// --------------------------------------------------
// Main test
// --------------------------------------------------

export default function (data) {

  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${data.accessToken}`,
      'Content-Type': 'application/json',
    },
  };


  // --------------------------------------------------
  // Create post
  // --------------------------------------------------

  const payload = JSON.stringify({
    text: 'This post includes media for performance testing.',
    long_text:
      'This is a longer description that should be accepted.',
    reference_link: 'https://example.com/post',
    post_user_visibility: 'public',
  });


  const postResponse = http.post(
    `${BASE_URL}/post`,
    payload,
    authHeaders
  );


  check(postResponse, {
    'POST /post: 200': (r) => r.status === 200,
  });


  if (postResponse.status !== 200) {
    console.log(
      `POST /post failed: ${postResponse.status}`
    );
    console.log(postResponse.body);
  }
}