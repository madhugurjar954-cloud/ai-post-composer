# AI Post Composer (MVP)

Simple Chrome extension MVP for composing social posts quickly using templates and presets.

What this does
- Popup UI with platform, type, tone, and context
- Generates template-based posts client-side (no external API)
- Copy to clipboard and small memory of last generated post

How to run locally (test)
1. Clone this repo.
2. Open Chrome → chrome://extensions
3. Enable 'Developer mode'
4. Click 'Load unpacked' and choose the repo folder
5. Click the extension icon to test

How to publish
- To publish on Chrome Web Store you need a developer account (one-time $5 USD fee).
- Build a zip of the extension files and follow the Chrome Web Store developer dashboard.

Landing page and Gumroad
- Edit `landing/index.html` in `landing/` (provided) to add your Gumroad link.
- Use Gumroad to sell a lifetime deal and link the buy button to Gumroad.

Next steps (after first sales)
1. Integrate OpenAI or other LLM to generate posts dynamically (requires API key and paid usage).
2. Add scheduling & paste‑to‑tab functionality (requires extra permissions).
3. Implement a Pro mode (premium templates) behind Gumroad or Stripe.

License: MIT
