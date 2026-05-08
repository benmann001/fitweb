# FitWeb — landing page

Static site. No build step, no framework. Open `index.html` in a browser to view; deploy to any static host.

## Brand reference

| Token        | Value      | Used for                                  |
|--------------|------------|-------------------------------------------|
| Ink          | `#0F0F0E`  | Primary dark surfaces, body text on chalk |
| Chalk        | `#F2F1ED`  | Primary light surface, body text on ink   |
| Steel        | `#6B6F75`  | Secondary text, captions                  |
| Concrete     | `#C7C6C0`  | Hairlines, muted UI                       |
| Signal       | `#E8FF3A`  | Single accent — CTAs, ticks, highlights   |

| Type         | Family                                   | Use                              |
|--------------|------------------------------------------|----------------------------------|
| Display      | Instrument Serif (Google Fonts, free)    | Hero, section heads, pull-quotes |
| Body / UI    | Geist Sans (Google Fonts, free)          | Body, buttons, nav               |
| Technical    | Geist Mono (Google Fonts, free)          | Eyebrows, prices, metadata       |

All design tokens live as CSS custom properties at the top of `styles.css` (`:root { --ink: ... }`). Change them once and the whole site shifts.

## Structure

```
fitweb-site/
├── index.html              ← markup, meta tags, JSON-LD schema
├── styles.css              ← all styles
├── script.js               ← nav, menu, FAQ, reveal-on-scroll, form
├── favicon.svg             ← brand monogram
├── sitemap.xml             ← single-URL sitemap
├── robots.txt              ← allow-all, references sitemap
├── README.md               ← this file
└── assets/
    ├── founder.jpg         ← brand-treated portrait of Ben (used in Founder section)
    └── process-portrait.py ← Python script that generated founder.jpg
```

## Editing common things

Each section is delimited in `index.html` by a comment block (`<!-- ──── Section ──── -->`) so you can find the right place fast.

**Hero copy** — Search for `class="hero__headline"`. Three lines wrapped in `<span class="reveal-line">` — the rise animation expects exactly that structure. Italic emphasis goes in `<em>...</em>`.

**Six-segment grid** — Search for `class="audiences__grid"`. Each `<article class="audience">` is one segment.

**Portfolio** — Search for `class="work__grid"`. Each `<article class="work-item">` is one project. Add `work-item--wide` (full-row hero) or `work-item--small` (3-up small) modifier classes for layout variants. Replace the placeholder block (`work-item__frame`) with an `<img>` tag once screenshots are ready:
```html
<a href="..." class="work-item__frame">
  <img src="assets/work/exercise-nz.jpg" alt="Exercise NZ — homepage">
</a>
```

**Packages & pricing** — Search for `class="packages__grid"`. Three `<article class="pkg">` blocks; the middle has `pkg--featured`. Pricing is hardcoded in `<strong>NZ$5.8k</strong>` — also update the matching JSON-LD prices in `<head>` so the schema stays accurate.

**Testimonials** — Search for `class="testimonial-grid"`. Currently 2-up; add a third `<article class="testimonial">` and the layout adapts.

**FAQ** — Search for `class="faq__list"`. Each `<div class="faq__item">` is a Q+A. Also update the matching `FAQPage` schema in the JSON-LD block in `<head>`.

**Founder photo** — Drop a new portrait at `/Users/Ben/Desktop/ben-mann-portrait.png` (or edit the path in the Python script) then run:
```bash
python3 assets/process-portrait.py
```
Outputs the brand-treated JPG to `assets/founder.jpg`. Requires `Pillow` and `numpy` (`pip3 install Pillow numpy`).

## Form backend

The enquiry form posts to **Formspree** at `https://formspree.io/f/xjglejod`. Submissions land in the configured Formspree inbox; nothing else needs wiring.

To switch backends later:
- **Netlify Forms** — change `action` to `/` and add `data-netlify="true"` to the `<form>` tag.
- **Cloudflare / Vercel Functions** — point `action` at your serverless endpoint that reads `name`, `business`, `email`, `package`, `message`. Ignore the `website` field (honeypot — bots fill it, humans don't).

The JS submits via `fetch` and shows inline status. With JS disabled, the form falls back to native browser submission to the same endpoint.

## OG image

`assets/og-image.jpg` is the social-share preview (1200×630, ink + signal-yellow editorial). Re-generate after copy or palette changes:
```bash
python3 assets/build-og-image.py
```
The script downloads Instrument Serif from Google Fonts on first run (cached in `assets/.fonts/`) so the OG image type matches the live site exactly. Requires `Pillow` and `numpy`.

## Deployment

Drop the entire folder onto any static host:

- **Cloudflare Pages** — `Connect to Git` → repo → no build command needed → publish directory: project root.
- **Netlify** — drag-and-drop the folder at app.netlify.com.
- **Vercel** — `vercel deploy` from inside the folder.
- **GitHub Pages** — push to a repo, enable Pages on the main branch root.
- **Plain hosting (e.g. cPanel)** — upload all files to the web root.

Update `<link rel="canonical">`, `og:url`, `og:image`, and the JSON-LD URLs in `index.html` if the production URL is anything other than `https://fitweb.co.nz/`.

## Performance & accessibility

- Lighthouse target: 95+ across all four scores. Achieved in baseline; will hold provided you don't add unoptimised hero images.
- All images need explicit `width`/`height` to prevent layout shift (CLS). The `founder.jpg` already has these set.
- Portfolio screenshots when added: serve as `.webp` or compressed JPEG, max ~250 KB each. Add `loading="lazy"` to anything below the fold.
- Skip-link, focus states, semantic landmarks, ARIA on accordion + menu, and `prefers-reduced-motion` overrides are all wired.
- Colour contrast: Chalk on Ink and Ink on Chalk both clear AAA. Signal on Ink clears AA at 18px+; don't use Signal as body-text colour.

## Quick local preview

```bash
cd fitweb-site
python3 -m http.server 8000
# then open http://localhost:8000
```

Or just double-click `index.html`.
