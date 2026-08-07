# RELEASE_INSTRUCTIONS.md

This file contains exact commands and steps to create the ai-post-composer.zip and prepare assets for Gumroad/Product Hunt.

1) Create the ZIP (copy/paste commands)

If you have the repo locally:

```bash
git clone https://github.com/madhugurjar954-cloud/ai-post-composer.git
cd ai-post-composer
zip -r ai-post-composer.zip manifest.json popup.html popup.js background.js styles.css icons/ landing/ INSTALL.md
```

If you don't have a terminal:
- On GitHub repo page click Code → Download ZIP. Rename the downloaded file to `ai-post-composer.zip`.

2) Verify ZIP contents
- Unzip locally and ensure these files are at root of the unzipped folder: manifest.json, popup.html, popup.js, styles.css, icons/
- Ensure INSTALL.md is included in zip.

3) Create Gumroad product
- Go to https://gumroad.com and sign in
- Products → New product → Digital product
- Title: AI Post Composer — Lifetime MVP
- Price: $19
- Upload ai-post-composer.zip as the product file
- Description (paste from RELEASE_NOTES/GUMROAD_DESC.md)
- Add screenshots (see /assets) and the install GIF (optional)
- Publish and copy the Gumroad link

4) Update repo buy links (if you want me to do this)
- Replace `REPLACE_WITH_GUMROAD_LINK` in `landing/index.html` and `popup.html` with your Gumroad URL and commit.
- Or paste your Gumroad link here and I will update and push the change for you.

5) Create a GitHub Release (optional)
- On GitHub repo page → Releases → Draft a new release
- Tag: v0.1.0
- Title: Initial MVP release - ai-post-composer.zip
- Attach the `ai-post-composer.zip` file to the release (upload)

6) Product Hunt assets
- Convert SVGs in /assets to PNG (1200×900) using ImageMagick or an online tool
- Create a 10–15s install GIF showing chrome://extensions → Developer mode → Load unpacked → open popup

7) Test purchase
- Create and publish the Gumroad product
- Make a test purchase (use your own card) and verify the ZIP downloads and INSTALL.md is present
- Follow the INSTALL.md to install the unpacked extension on another machine to confirm buyer experience

8) Launch schedule
- Pick a launch day (Tue/Wed/Thu morning PST). I recommend launching within 3–5 days of creating Gumroad and assets.


GUMROAD_DESC.md and PH_POST.md are available in the repo for copy/paste of product descriptions and Product Hunt text.
