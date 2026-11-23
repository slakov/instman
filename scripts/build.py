"""Build the bilingual site using Python 3.11+ and the standard library."""
import argparse
import shutil
import tomllib
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("ru", "en")
NAV = ("about", "research", "center", "materials", "participate")
SCENARIOS = ("join", "idea", "challenge", "question")
PATHS = ("materials/", "participate/?scenario=join#worksheet", "participate/?scenario=idea#worksheet", "participate/?scenario=challenge#worksheet")


def content(lang, name):
    with (ROOT / "content" / lang / (name + ".toml")).open("rb") as file:
        return tomllib.load(file)


def template(name, values):
    source = (ROOT / "templates" / (name + ".html")).read_text()
    return Template(source).substitute(values)


def text_fields(data):
    return {k: escape(v) for k, v in data.items() if isinstance(v, str)}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def anchor(label, url, attrs=""):
    return f'<a href="{escape(url)}"{attrs}>{escape(label)}</a>'


def links(items, local):
    if not items:
        return ""
    result = []
    for label, url in items:
        href = url if url.startswith("https://") else local + url
        result.append(anchor(label, href, ' class="text-link"'))
    return '<div class="link-row">' + "".join(result) + "</div>"


def home(page, site, local, base):
    def card(title, body):
        return f'<article><h3>{escape(title)}</h3><p>{escape(body)}</p></article>'

    domain_cards = [card(a, b) for a, b in zip(page["domains"], page["questions"], strict=True)]
    form_cards = [card(a, b) for a, b in zip(page["forms"], page["form_text"], strict=True)]
    options = []
    for label, desc, path in zip(page["paths"], page["path_text"], PATHS, strict=True):
        options.append(f'<article class="route"><h3>{anchor(label, local + path)}</h3><p>{escape(desc)}</p></article>')
    return template("home", {
        **text_fields(site), **text_fields(page), "local": local, "base": base,
        "mission": "".join(f"<span>{escape(word)}</span>" for word in page["mission"]),
        "domains": "".join(domain_cards), "paths": "".join(options), "forms": "".join(form_cards),
        "links": links(zip(page["links"], ("research/", "center/"), strict=True), local),
    })


def section_html(section, local):
    paragraphs = "".join(f"<p>{escape(p)}</p>" for p in section.get("body", []))
    items = "".join(f"<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>" for k, v in section.get("items", []))
    ident = escape(section["id"])
    return (f'<section id="{ident}"><h2>{escape(section["title"])}</h2>{paragraphs}'
            + (f"<dl>{items}</dl>" if items else "") + links(section.get("links"), local) + "</section>")


def material_list(lang, page, local):
    rows = []
    for slug in page["note_ids"]:
        note = content(lang, "notes/" + slug)
        title = anchor(note["title"], f"{local}materials/{slug}/")
        rows.append(f'<article><p class="eyebrow">{escape(note["kind"])}</p><h2>{title}</h2>'
                    f'<p>{escape(note["intro"])}</p><p class="status">{escape(note["status"])} · v1.0 · 2026-11-23</p></article>')
    return '<div class="material-list">' + "".join(rows) + "</div>"


def worksheet(lang, page, local):
    p = text_fields(page)
    options = "".join(f'<option value="{key}" data-prompt="{escape(hint)}">{escape(title)}</option>'
                      for key, title, hint in zip(SCENARIOS, page["scenarios"], page["prompts"], strict=True))
    prompts = "".join(f"<dt>{escape(title)}</dt><dd>{escape(hint)}</dd>"
                     for title, hint in zip(page["scenarios"], page["prompts"], strict=True))
    required = "Напишите несколько слов для черновика." if lang == "ru" else "Write a few words for your draft."
    return f'''<div class="notice"><h2>{p["contact"]}</h2><p>{p["notice"]}</p>
      {links([(page["browse"], "materials/")], local)}</div>
      <div class="worksheet" id="worksheet"><label for="scenario">{p["choose"]}</label><select id="scenario">{options}</select>
      <p class="scenario-prompt" aria-live="polite">{escape(page["prompts"][0])}</p>
      <label for="draft">{p["draft"]}</label><p id="draft-hint" class="hint">{p["hint"]}</p>
      <textarea id="draft" aria-describedby="draft-hint" data-required="{required}"></textarea>
      <button type="button" class="button navy" hidden>{p["save"]}</button><noscript><dl>{prompts}</dl><p>{p["noscript"]}</p></noscript>
      <p role="status" data-saved="{p["saved"]}"></p></div>'''


def article(lang, slug, page, site, local):
    sections = page.get("section", [])
    sidebar = ""
    status = ""
    parent = ""
    body = "".join(section_html(section, local) for section in sections)
    if sections:
        items = "".join(anchor(s["title"], "#" + s["id"]) for s in sections)
        sidebar = f'<nav class="aside" aria-label="{escape(site["contents"])}"><p class="eyebrow">{escape(site["contents"])}</p>{items}</nav>'
    if slug == "materials":
        body = material_list(lang, page, local)
    if slug == "participate":
        body = worksheet(lang, page, local)
    if "source" in page:
        parent = '<span aria-hidden="true">/</span>' + anchor(site["materials"], local + "materials/")
        status = f'<p class="status">{escape(page["kind"])} · {escape(page["status"])}</p>'
        body += f'<div class="credit"><strong>{escape(site["source"])}</strong><p>{escape(page["source"])}</p></div>'
    return template("article", {**text_fields(site), **text_fields(page), "local": local, "parent": parent,
                    "status": status, "layout": "" if sections else " single", "sidebar": sidebar, "body": body})


def metadata(origin, path, preview):
    if preview:
        return '<meta name="robots" content="noindex,nofollow">'
    slug = path.partition("/")[2]
    rels = [f'<link rel="canonical" href="{escape(origin + path)}">']
    for lang in LANGS:
        rels.append(f'<link rel="alternate" hreflang="{lang}" href="{escape(origin + lang + "/" + slug)}">')
    return "\n  ".join(rels)


def build(output, origin, preview):
    locales = {lang: content(lang, "site") for lang in LANGS}
    ids = {lang: content(lang, "materials")["note_ids"] for lang in LANGS}
    if ids["ru"] != ids["en"]:
        raise ValueError("Each material must have a matching RU and EN version")
    pages = {"": "home", **{slug + "/": slug for slug in (*NAV, "privacy")}}
    pages.update({f"materials/{slug}/": "notes/" + slug for slug in ids["ru"]})
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "assets", output / "assets", dirs_exist_ok=True)
    sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for lang, site in locales.items():
        for slug, name in pages.items():
            path = f"{lang}/{slug}"
            base = "../" * path.count("/")
            local = base + lang + "/"
            page = content(lang, name)
            nav = "".join(anchor(label, local + section + "/", ' aria-current="page"' if slug == section + "/" else
                                 ' aria-current="location"' if slug.startswith(section + "/") else "")
                          for section, label in zip(NAV, site["nav"], strict=True))
            switches = "".join(f'<strong lang="{code}" aria-current="true">{code.upper()}</strong>' if code == lang else
                               anchor(code.upper(), base + code + "/" + slug, f' lang="{code}" hreflang="{code}"')
                               for code in LANGS)
            main = home(page, site, local, base) if not slug else article(lang, slug.rstrip("/"), page, site, local)
            html = template("page", {**text_fields(site), "base": base, "local": local, "lang": lang, "nav": nav,
                            "title": escape(page["title"]), "description": escape(page["intro"]),
                            "language_links": switches, "main": main, "metadata": metadata(origin, path, preview)})
            write(output / path / "index.html", html)
            ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = origin + path
    write(output / ".nojekyll", "")
    # The catch-all document can be served from any depth by Pages.
    root_url = escape(urlsplit(origin).path)
    for is_error in (False, True):
        title = "Страница не найдена / Page not found" if is_error else "Институт человека / Institute of the Human"
        attrs = "" if is_error else ' data-entry="true"'
        prefix = root_url if is_error else "./"
        script = "" if is_error else '<script defer src="./assets/site.js"></script>'
        robots = '<meta name="robots" content="noindex">' if is_error or preview else ""
        buttons = " ".join(anchor(label, prefix + lang + "/", f' lang="{lang}" hreflang="{lang}" data-entry class="button navy"')
                           for label, lang in (("Русский", "ru"), ("English", "en")))
        html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
        <link rel="icon" href="data:,"><link rel="stylesheet" href="{prefix}assets/site.css">{robots}{script}</head><body{attrs}>
        <main class="wrap endcap"><div><h1>{title}</h1><nav class="link-row" aria-label="Язык / Language">{buttons}</nav></div></main></body></html>'''
        write(output / ("404.html" if is_error else "index.html"), html)
    if not preview:
        ET.ElementTree(sitemap).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    write(output / "robots.txt", "User-agent: *\nDisallow: /\n" if preview else "User-agent: *\nAllow: /\nSitemap: " + origin + "sitemap.xml\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--url", default="https://slakov.github.io/instman/")
    parser.add_argument("--preview", action="store_true", help="Discourage indexing of a preview build")
    args = parser.parse_args()
    build(args.output, args.url.rstrip("/") + "/", args.preview)
