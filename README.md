# University / Institute of the Human

A bilingual public introduction to an initiative in development. The Russian and English editions have equivalent pages under `/ru/` and `/en/`. The root opens Russian on a first visit and remembers a visitor’s subsequent choice. Reading and navigation work without JavaScript.

## Edit and preview

Edit the matching TOML files under `content/ru/` and `content/en/` in GitHub’s file editor or a local checkout. Text in quotation marks is public copy. Keep section IDs and note filenames aligned across languages. Open a pull request to review both editions. The build produces a downloadable preview artifact with indexing disabled. Only add material or images cleared for the public site.

Build locally with Python 3.11 or later. The generator uses the standard library and makes no network requests. Use a fresh output directory when removing or renaming published material.

```sh
python3 scripts/build.py
python3 scripts/check.py _site
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000/ru/` or `http://localhost:8000/en/`. For a preview, use `python3 scripts/build.py --preview --output _preview`. The repository is the editable source and version history. To restore an earlier edition, revert the relevant commit on a branch, review it, then merge. A clean checkout of an earlier revision can also rebuild the entire publication offline.

## GitHub Pages

The workflow builds, checks and publishes static HTML on pushes to `main`. Select **Settings → Pages → Build and deployment → GitHub Actions** once for the repository. The publication URL is `https://slakov.github.io/instman/`. Check the **Bilingual website** workflow and the `github-pages` deployment for failures. New builds run in a clean directory, so withdrawing a page and its links removes it from the next publication.

## Editorial decisions for this edition

- The name is provisional. The text-based header uses the shorter Institute name. The homepage gives the full working name.
- The theme uses the written historical guide’s navy (`#0B2345`), ivory, slate and gold. The visual sheet’s alternate blue (`#0B2D5B`) remains an open branding decision. The historic emblem, architectural concepts, internal files and personal names are outside this publication.
- Enquiries are local text drafts. The site has no submission endpoint. A public recipient, operator and handling terms would be needed to introduce correspondence.
- The brief’s comprehension test still requires someone unfamiliar with the project. Ask what the initiative is for, what harmonious development means here, what role the Center plays and where they would personally begin.

## Assets

The Wotton Oak, etching after Jacob George Strutt, 1823. Wellcome Collection, reference 18303i, Public Domain Mark. The museum scan is served locally as WebP. [Catalogue record](https://wellcomecollection.org/works/gcjezqme)

Playfair Display and Montserrat are served locally in WOFF2. Their SIL Open Font License texts are in `assets/fonts/`. [Playfair Display](https://github.com/google/fonts/tree/main/ofl/playfairdisplay) · [Montserrat](https://github.com/google/fonts/tree/main/ofl/montserrat)
