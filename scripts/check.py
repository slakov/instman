"""Check the generated site, including links when hosted under a project prefix."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import urljoin, urlsplit

PREFIX = "/instman/"
ORIGIN = "https://slakov.github.io"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = []
        self.ids = set()
        self.lang = ""
        self.alternates = {}
        self.headings = 0
        self.canonical = None
        self.noindex = False
        self.feed(path.read_text())
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs["lang"]
        if tag == "h1":
            self.headings += 1
        if tag == "img":
            assert attrs.get("alt") and attrs.get("width") and attrs.get("height")
        if tag == "link" and attrs.get("rel") == "alternate":
            self.alternates[attrs["hreflang"]] = attrs["href"]
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs["href"]
        if tag == "meta" and attrs.get("name") == "robots":
            self.noindex = "noindex" in attrs["content"]
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])


def check(root):
    documents = {p: Page(root / p) for p in (f.relative_to(root) for f in root.rglob("*.html"))}
    assert Path("index.html") in documents and Path("404.html") in documents
    for path, page in documents.items():
        assert page.headings == 1, path
        base = ORIGIN + PREFIX + str(path)
        if path.parts[0] in ("ru", "en"):
            lang = path.parts[0]
            assert page.lang == lang, path
            other = "en" if lang == "ru" else "ru"
            twin = Path(other, *path.parts[1:])
            assert twin in documents and documents[twin].ids == page.ids, path
            if not page.noindex:
                assert page.canonical == base.removesuffix("index.html"), path
                assert page.alternates == {locale: ORIGIN + PREFIX + str(Path(locale, *path.parts[1:])).removesuffix("index.html") for locale in ("ru", "en")}, path
        for link in page.links:
            url = urlsplit(urljoin(base, link))
            if url.scheme == "data" or url.netloc != "slakov.github.io":
                continue
            assert url.path.startswith(PREFIX), (path, link)
            target = Path(url.path.removeprefix(PREFIX))
            if url.path.endswith("/"):
                target /= "index.html"
            assert (root / target).is_file(), (path, link)
            if url.fragment:
                assert target in documents and url.fragment in documents[target].ids, (path, link)
    print(f"Verified {len(documents)} documents, language pairs, metadata, local links and fragments.")


if __name__ == "__main__":
    check(Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve())
