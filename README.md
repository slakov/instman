# Институт человека · Institute of the Human

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

- The public working name is **Институт человека / Institute of the Human** in both the masthead and the body. The About page records its provisional status. The typography and navy-and-gold palette define this web edition; an official emblem and institutional identity still await approval.
- The public mailbox belongs to the Institute. Set it once in `content/contact.toml`. The participation page opens an addressed email in the visitor’s own mail application. Visitors using webmail can copy the address and message. The site has no backend, collects no draft text and gives no delivery confirmation.
- Materials identify external primary research, a reproducible mathematical example and editorial guides at list level. Each entry has a dated credit. Keep both language versions in sync. The two-clock example includes source code and its generated CSV in `assets/studies/phase-locking/`.
- The brief’s comprehension test still requires someone unfamiliar with the project. Ask what the initiative is for, what harmonious development means here, what role the Center plays and where they would personally begin.

## Assets

The Wotton Oak, etching after Jacob George Strutt, 1823. Wellcome Collection, reference 18303i, Public Domain Mark. The museum scan is served locally as WebP. [Catalogue record](https://wellcomecollection.org/works/gcjezqme)

Source Sans 3 is self-hosted in WOFF2 with Cyrillic and Latin coverage. The font is distributed under the SIL Open Font License 1.1; its license is in `assets/fonts/SourceSans3-OFL.txt`. [Adobe Source Sans](https://github.com/adobe-fonts/source-sans)
