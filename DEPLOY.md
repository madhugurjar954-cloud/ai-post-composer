# DEPLOY.md

How to deploy the serverless functions (Vercel) and set environment variables.

1) Sign up for Vercel (https://vercel.com) if you don't have an account.

2) Deploy the repo
- Option A (recommended): Connect your GitHub account in Vercel and import the repository `madhugurjar954-cloud/ai-post-composer`. Vercel will detect the `api/` folder and create serverless endpoints at `https://<your-project>.vercel.app/api/generate` and `/api/checkLicense`.
- Option B: Deploy via the Vercel CLI or use Netlify functions (adjust function format accordingly).

3) Add environment variables in your Vercel project settings
- OPENAI_API_KEY : <your OpenAI API key>
- LICENSE_KEYS : comma-separated license keys for initial sales (e.g. "key-abc123,key-xyz789") — optional. If this is empty, server will allow generation without license enforcement (development mode).

4) After deploy, copy the Vercel base URL (for example `https://ai-post-composer.vercel.app`) and paste it into the extension's API base field (in the popup) and save.

5) Test the endpoints
- Check License:
  POST https://<your-base>/api/checkLicense
  Body: { "license": "key-abc123" }
- Generate:
  POST https://<your-base>/api/generate
  Body: { "platform": "linkedin", "type": "short", "tone": "professional", "context": "CS50 project", "length": 3, "license": "key-abc123" }

6) Open the extension (Load unpacked if testing locally), set the API base to your Vercel URL, paste your license key, press Activate, then use "Generate (AI)".

Notes on OpenAI costs
- You are responsible for OpenAI usage charges for requests made through the server. Start with a small test budget ($5–$20) to tune prompts and usage. Monitor usage in your OpenAI dashboard.

Security notes
- Never commit your OPENAI_API_KEY to the repo.
- Set env vars in Vercel only.
