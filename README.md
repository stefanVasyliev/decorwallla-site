# DecorWall LA — website source

Site: https://decorwallla.com (Porkbun Secure Static Hosting)

## How it works
- `build.py` + `data_cities.py` / `data_services.py` / `data_styles.py` — the generator and content data.
- `assets/` — images and styles used by the generator.
- `dist/` — the built site (539 pages). This is exactly what gets uploaded to the hosting.

## Making changes
1. Edit the generator or data files (never edit `dist/` by hand).
2. Run `python3 build.py` to rebuild `dist/`.
3. Upload the changed files from `dist/` to Porkbun hosting (FTP: pixie-ss1-ftp.porkbun.com, user decorwallla.com).
4. Commit the change here so every edit is tracked.

Lead form on the site posts to hello@decorwallla.com via FormSubmit.
