#!/usr/bin/env python3
"""
SEO Page Analyzer — Extract SEO and conversion elements from any webpage.
Absorbed from OpenClaw → now a native Ouroboros tool.
"""

import sys
import json
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser
from urllib.parse import urlparse


class SEOPageParser(HTMLParser):
    """Extract SEO and conversion elements from HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.meta_keywords = ""
        self.og_title = ""
        self.og_description = ""
        self.og_type = ""
        self.og_image = ""
        self.h1_tags = []
        self.h2_tags = []
        self.h3_tags = []
        self.images = []
        self.links_internal = []
        self.links_external = []
        self.ctas = []
        self.forms = []
        self.canonical_url = ""
        self.robots = ""
        self.viewport = ""
        self.schema_count = 0
        self.scripts = []
        self.internal_links = 0
        self.external_links = 0
        self.word_count = 0

        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_h3 = False
        self._current_text = ""
        self._domain = ""
        self._all_text = []

    def set_domain(self, url):
        parsed = urlparse(url)
        self._domain = parsed.netloc

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self._in_title = True
            self._current_text = ""
        elif tag in ("h1", "h2", "h3"):
            if tag == "h1": self._in_h1 = True
            elif tag == "h2": self._in_h2 = True
            elif tag == "h3": self._in_h3 = True
            self._current_text = ""
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            http_equiv = attrs_dict.get("http-equiv", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif name == "keywords":
                self.meta_keywords = content
            elif name == "viewport":
                self.viewport = content
            elif name == "robots":
                self.robots = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
            elif prop == "og:type":
                self.og_type = content
            elif prop == "og:image":
                self.og_image = content
        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            if "canonical" in rel:
                self.canonical_url = href
        elif tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            loading = attrs_dict.get("loading", "")
            width = attrs_dict.get("width", "")
            height = attrs_dict.get("height", "")
            self.images.append({
                "src": src, "alt": alt, "loading": loading,
                "width": width, "height": height, "has_alt": bool(alt.strip()),
                "has_dimensions": bool(width and height)
            })
        elif tag == "a":
            href = attrs_dict.get("href", "")
            text = ""
            self._in_a = True
            self._a_href = href
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                if self._domain and self._domain in href:
                    self.links_internal.append(href)
                    self.internal_links += 1
                elif href.startswith("http"):
                    self.links_external.append(href)
                    self.external_links += 1
        elif tag == "form":
            action = attrs_dict.get("action", "")
            method = attrs_dict.get("method", "get")
            self.forms.append({"action": action, "method": method})
        elif tag == "button":
            self._in_button = True
            self._current_text = ""
        elif tag == "script":
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
                # Detect tracking
                if any(t in src.lower() for t in ["google-analytics", "gtag", "googletagmanager",
                                                    "facebook", "fbq", "hotjar", "pixel", "analytics"]):
                    pass  # Tracked

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = self._current_text.strip()
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            t = self._current_text.strip()
            if t: self.h1_tags.append(t)
        elif tag == "h2" and self._in_h2:
            self._in_h2 = False
            t = self._current_text.strip()
            if t: self.h2_tags.append(t)
        elif tag == "h3" and self._in_h3:
            self._in_h3 = False
            t = self._current_text.strip()
            if t: self.h3_tags.append(t)
        elif tag == "a":
            pass
        elif tag == "button":
            t = self._current_text.strip()
            if t:
                cta_words = ["sign up", "get started", "try", "start", "buy", "subscribe",
                             "join", "register", "download", "book", "demo", "contact",
                             "pricing", "add to cart", "configure", "customizer", "créer"]
                if any(w in t.lower() for w in cta_words):
                    self.ctas.append(t)

    def handle_data(self, data):
        if self._in_title or self._in_h1 or self._in_h2 or self._in_h3 or getattr(self, '_in_button', False):
            self._current_text += data
        self._all_text.append(data.strip())

    @property
    def text_content(self):
        return " ".join(t for t in self._all_text if t)

    def get_results(self):
        full_text = self.text_content
        words = len(full_text.split())
        images_without_alt = sum(1 for img in self.images if not img["has_alt"])
        images_without_dims = sum(1 for img in self.images if not img["has_dimensions"])
        
        # Detect tracking scripts
        tracking = [s for s in self.scripts if any(t in s.lower() 
                    for t in ["google", "ga", "analytics", "facebook", "fbq", 
                              "pixel", "hotjar", "tagmanager", "gtm"])]
        
        # Check for tracking in data attributes too
        has_ga4 = any("gtag" in s or "googletagmanager" in s for s in tracking)
        has_gtm = any("googletagmanager" in s or "gtm" in s for s in tracking)
        has_fb_pixel = any("facebook" in s or "fbq" in s or "fbpixel" in s for s in tracking)
        has_hotjar = any("hotjar" in s for s in tracking)

        return {
            "seo": {
                "title": self.title,
                "title_length": len(self.title),
                "meta_description": self.meta_description,
                "meta_description_length": len(self.meta_description),
                "meta_keywords": self.meta_keywords,
                "h1_count": len(self.h1_tags),
                "h1_tags": self.h1_tags,
                "h2_count": len(self.h2_tags),
                "h3_count": len(self.h3_tags),
                "canonical_url": self.canonical_url,
                "robots": self.robots,
                "viewport": self.viewport,
                "schema_scripts": self.schema_count,
                "word_count": words,
            },
            "images": {
                "total": len(self.images),
                "missing_alt": images_without_alt,
                "missing_dimensions": images_without_dims,
            },
            "links": {
                "internal": self.internal_links,
                "external": self.external_links,
            },
            "ctas": self.ctas,
            "forms": self.forms,
            "tracking": {
                "scripts": tracking,
                "ga4": has_ga4,
                "gtm": has_gtm,
                "facebook_pixel": has_fb_pixel,
                "hotjar": has_hotjar,
            }
        }


def analyze_page(url):
    """Fetch and analyze a page for SEO elements."""
    if not url.startswith("http"):
        url = "https://" + url

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e), "url": url}

    parser = SEOPageParser()
    parser.set_domain(url)
    try:
        parser.feed(html)
    except Exception as e:
        return {"error": str(e), "url": url}

    results = parser.get_results()
    results["url"] = url
    return results


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 analyze_page.py <url>",
            "example": "python3 analyze_page.py https://sklubs.fr/",
            "description": "Extract SEO elements from a webpage"
        }, indent=2))
        return

    url = sys.argv[1]
    result = analyze_page(url)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
