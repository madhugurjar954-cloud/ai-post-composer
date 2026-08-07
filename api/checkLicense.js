// vercel/api/checkLicense.js

// Simple serverless license verification function.
// POST JSON: { license }
// Env: LICENSE_KEYS (comma-separated)

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const { license } = req.body || {};
  const licenseKeys = (process.env.LICENSE_KEYS || '').split(',').map(s => s.trim()).filter(Boolean);
  if (licenseKeys.length === 0) {
    // No license enforcement configured on server — accept any key (development mode)
    res.status(200).json({ valid: true, message: 'No license enforcement configured on server' });
    return;
  }
  if (license && licenseKeys.includes(license)) {
    res.status(200).json({ valid: true });
  } else {
    res.status(200).json({ valid: false });
  }
}
