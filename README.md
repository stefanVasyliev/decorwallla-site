# DecorWall LA

Website for DecorWall LA: media walls, slat walls, stone and accent walls in Los Angeles.

## How it is built
- `index.html` is the home page, built by hand (hero, wall builder, packages).
- `site/build.py` generates every other page (services, styles, 86 cities x 5 services, cost, process, FAQ...)
  in the same design, and fills the home page's header, extra blocks and footer.
- `site/data/` holds the content (cities, services, styles, FAQ variants). It is read as plain data.
- `assets/site.css` and `assets/site.js` are shared by every page; `assets/styles/` and `assets/projects/` hold the
  full-resolution photos; `images/` holds the home page photos and material textures.

## Build
```
python3 site/build.py            # dist/     clean URLs, upload this folder to the hosting
python3 site/build.py --preview  # preview/  relative links, opens straight from the files
```
Lead forms post to hello@decorwallla.com via FormSubmit.

## Still to do
- WhatsApp: set `WHATSAPP` in `site/build.py` (digits with country code). Until then the WhatsApp buttons open
  WhatsApp with the message ready but no recipient.
- Wall builder: the project and style starting prices are real; the add-on prices are placeholders at the top of
  the last `<script>` in `index.html`.
- The home perks (Free / Custom / Local) and copy carried over from the old site should be checked.
- Suisse Int'l is a licensed font; until its files are added, Geist is used instead.
