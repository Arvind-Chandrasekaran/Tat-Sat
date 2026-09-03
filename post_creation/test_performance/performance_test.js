import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  duration: '30s',

  thresholds: {
    http_req_failed: ['rate<0.01'],
  },
};



const BASE_URL = __ENV.POST_CREATION_DEPLOYED_URL;
const SUPABASE_URL = __ENV.SUPABASE_PROJECT_URL;
const SUPABASE_KEY = __ENV.SUPABASE_PUBLISHABLE_KEY;
const TEST_USER_EMAIL = __ENV.TEST_USER_EMAIL;
const TEST_USER_PASSWORD = __ENV.TEST_USER_PASSWORD;

const testImage = open('./test_img.jpg', 'b');
const testVideo = open('./test_vid.mp4', 'b');





export function setup() {

  // Authenticate with Supabase
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



export default function (data) {

  const authHeaders = {
    headers: {
      'Authorization': `Bearer ${data.accessToken}`,
    },
  };



  
  // --------------------------------------------------
  // 1. Get signed upload URLs
  // --------------------------------------------------

  const mediaResponse = http.get(
    `${BASE_URL}/post-media-urls`,
    authHeaders
  );

  check(mediaResponse, {
    'GET /post-media-urls: 200': (r) => r.status === 200,
  });

  if (mediaResponse.status !== 200) {
    console.log(
      `GET /post-media-urls failed: ${mediaResponse.status}`
    );
    console.log(mediaResponse.body);
    return;
  }


  const mediaData = mediaResponse.json();

  const signedUploads = mediaData.signed_upload_urls;

  if (!signedUploads || signedUploads.length < 2) {
    console.log('Did not receive at least 2 signed upload URLs');
    console.log(mediaResponse.body);
    return;
  }






  // --------------------------------------------------
  // 2. Upload image
  // --------------------------------------------------

  const imageUpload = signedUploads[0];

  const imageResponse = http.put(
    imageUpload.signed_url,
    testImage,
    {
      headers: {
        'Content-Type': 'image/JPEG',
      },
    }
  );

  check(imageResponse, {
    'Image upload successful': (r) =>
      r.status === 200 || r.status === 201,
  });

  if (imageResponse.status !== 200 && imageResponse.status !== 201) {
    console.log(
      `Image upload failed: ${imageResponse.status}`
    );
    console.log(imageResponse.body);
    return;
  }


  // --------------------------------------------------
  // 3. Upload video
  // --------------------------------------------------

  const videoUpload = signedUploads[1];

  const videoResponse = http.put(
    videoUpload.signed_url,
    testVideo,
    {
      headers: {
        'Content-Type': 'video/MP4',
      },
    }
  );

  check(videoResponse, {
    'Video upload successful': (r) =>
      r.status === 200 || r.status === 201,
  });

  if (videoResponse.status !== 200 && videoResponse.status !== 201) {
    console.log(
      `Video upload failed: ${videoResponse.status}`
    );
    console.log(videoResponse.body);
    return;
  }


  // --------------------------------------------------
  // 4. Create post
  // --------------------------------------------------

  const payload = JSON.stringify({
    text: 'This post includes uploaded media for performance testing.',
    long_text:
      'This is a longer description that should be accepted when the media is valid.',
    media_ids: [
      imageUpload.media_id,
      videoUpload.media_id,
    ],
    media_types: [
      'image',
      'video',
    ],
    reference_link: 'https://example.com/post',
    post_user_visibility: 'public',
  });


  const postResponse = http.post(
    `${BASE_URL}/post`,
    payload,
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.accessToken}`,
      },
    }
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