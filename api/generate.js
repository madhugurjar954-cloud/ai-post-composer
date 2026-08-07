// vercel/api/generate.js

// Serverless function for Vercel to proxy generation requests to OpenAI.
// Expects POST JSON: { platform, type, tone, context, length, license }
// Env vars required: OPENAI_API_KEY (your OpenAI key), LICENSE_KEYS (optional, comma-separated)

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { platform, type, tone, context, length, license } = req.body || {};

  // Simple license check if LICENSE_KEYS is set
  const licenseKeys = (process.env.LICENSE_KEYS || '').split(',').map(s => s.trim()).filter(Boolean);
  if (licenseKeys.length > 0) {
    if (!license || !licenseKeys.includes(license)) {
      res.status(403).json({ error: 'Invalid or missing license key' });
      return;
    }
  }

  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
  if (!OPENAI_API_KEY) {
    res.status(500).json({ error: 'OpenAI API key not configured on server' });
    return;
  }

  // Build a prompt for Chat API
  const userPrompt = `You are a helpful assistant that writes social media posts.
Platform: ${platform}
Type: ${type}
Tone: ${tone}
Context: ${context}
Length: ${length}

Produce one polished ${platform === 'twitter' ? 'thread-style' : 'post-style'} output appropriate for the platform.`;

  try {
    const resp = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: 'You generate concise social media posts based on the user instructions.' },
          { role: 'user', content: userPrompt }
        ],
        max_tokens: 400,
        temperature: 0.7
      })
    });

    if (!resp.ok) {
      const txt = await resp.text();
      res.status(resp.status).json({ error: 'OpenAI error', detail: txt });
      return;
    }

    const data = await resp.json();
    const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
    res.status(200).json({ text: content });
  } catch (err) {
    res.status(500).json({ error: 'Server error', detail: err.message });
  }
}
