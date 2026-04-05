#!/usr/bin/env python3
"""
analyze_page.py — SEO Audit Complet
Absorbed from OpenClaw ai-marketing-claude → Ouroboros
Usage: python analyze_page.py <url>

Analyse une page web et retourne un audit SEO complet :
- Meta tags (title, description, OG, canonical)
- Heading hierarchy (H1-H6)
- Images et alt text
- Liens internes/externes
- Performance indicators
- Schema markup
- Core Web Vitals estimations
"""

import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Requirements: pip install requests beautifulsoup4")
    sys.exit(1)


class SEOAnalyzer:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.html = ""
        self.soup = None
        self.issues = []
        self.warnings = []
        self.passes = []

    def fetch(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        response = requests.get(self.url, headers=headers, timeout=30)
        self.html = response.text
        self.soup = BeautifulSoup(self.html, "html.parser")
        return response

    def _add_issue(self, severity, category, message, recommendation):
        entry = {"severity": severity, "category": category, "message": message}
        if recommendation:
            entry["recommendation"] = recommendation
        if severity == "error":
            self.issues.append(entry)
        else:
            self.warnings.append(entry)

    def _add_pass(self, category, message):
        self.passes.append({"category": category, "message": message})

    def analyze_title(self):
        title_tag = self.soup.find("title")
        if not title_tag or not title_tag.get_text(strip=True):
            self._add_issue("error", "meta", "No title tag found", "Add a <title> tag with 50-60 characters")
            return None
        title = title_tag.get_text(strip=True)
        title_len = len(title)
        if title_len < 30:
            self._add_issue("warning", "meta", f"Title too short ({title_len} chars, target 50-60)", "Expand to 50-60 chars with primary keyword")
        elif title_len > 60:
            self._add_issue("warning", "meta", f"Title too long ({title_len} chars, target 50-60)", "Trim to 50-60 chars, keep keyword near start")
        else:
            self._add_pass("meta", f"Title length is good ({title_len} chars)")
        return title

    def analyze_meta_description(self):
        meta = self.soup.find("meta", attrs={"name": "description"})
        if not meta or not meta.get("content", "").strip():
            self._add_issue("error", "meta", "No meta description found", "Add unique meta description (150-160 chars) with CTA")
            return None
        desc = meta["content"].strip()
        desc_len = len(desc)
        if desc_len < 120:
            self._add_issue("warning", "meta", f"Meta description too short ({desc_len} chars)", "Expand to 150-160 chars")
        elif desc_len > 160:
            self._add_issue("warning", "meta", f"Meta description too long ({desc_len} chars)", "Trim to 150-160 chars")
        else:
            self._add_pass("meta", f"Meta description length is good ({desc_len} chars)")
        if desc.count(".") <= 0:
            self._add_issue("warning", "meta", "No sentence structure in description", "Add punctuation for readability")
        return desc

    def analyze_headings(self):
        headings = {}
        for level in range(1, 7):
            tags = self.soup.find_all(f"h{level}")
            headings[f"h{level}"] = [t.get_text(strip=True) for t in tags]

        h1_count = len(headings.get("h1", []))
        if h1_count == 0:
            self._add_issue("error", "headings", "No H1 tag found", "Add exactly one H1 with primary keyword")
        elif h1_count > 1:
            self._add_issue("warning", "headings", f"Multiple H1 tags found ({h1_count})", "Use exactly one H1 per page")
        else:
            self._add_pass("headings", f"One H1 found: '{headings['h1'][0][:60]}...'")

        # Check heading skip
        present_levels = [i for i in range(1, 7) if headings.get(f"h{i}")]
        for i in range(len(present_levels) - 1):
            if present_levels[i + 1] - present_levels[i] > 1:
                self._add_issue("warning", "headings",
                    f"Heading level skipped: h{present_levels[i]} → h{present_levels[i+1]}",
                    "Don't skip heading levels (H1→H2→H3)")

        return headings

    def analyze_images(self):
        images = self.soup.find_all("img")
        total = len(images)
        missing_alt = 0
        empty_alt = 0
        for img in images:
            alt = img.get("alt")
            if alt is None:
                missing_alt += 1
            elif alt.strip() == "":
                empty_alt += 1
        if missing_alt > 0:
            self._add_issue("error", "images", f"{missing_alt}/{total} images missing alt text", "Add descriptive alt text to all images")
        elif total == 0:
            self._add_issue("warning", "images", "No images found on page", "Add product/service images to increase engagement")
        else:
            self._add_pass("images", f"All {total} images have alt text")

        # Check lazy loading
        lazy_count = sum(1 for img in images if img.get("loading") == "lazy")
        if total > 3 and lazy_count == 0:
            self._add_issue("warning", "images", f"None of {total} images use lazy loading", "Add loading='lazy' to below-fold images")
        elif lazy_count > 0:
            self._add_pass("images", f"{lazy_count}/{total} images use lazy loading")

        return {"total": total, "missing_alt": missing_alt, "empty_alt": empty_alt}

    def analyze_links(self):
        links = self.soup.find_all("a", href=True)
        internal = []
        external = []
        for link in links:
            href = link["href"]
            if href.startswith(("http", "//")):
                link_domain = urlparse(href).netloc
                if link_domain and link_domain != self.domain:
                    external.append({"url": href, "text": link.get_text(strip=True)})
                else:
                    internal.append({"url": href, "text": link.get_text(strip=True)})
            else:
                internal.append({"url": href, "text": link.get_text(strip=True)})

        if len(internal) < 3 and len(internal) > 0:
            self._add_issue("warning", "links", f"Only {len(internal)} internal links", "Add 3-10 internal links per 1000 words")
        elif len(internal) >= 3:
            self._add_pass("links", f"{len(internal)} internal links found")

        # Check for generic anchor text
        generic = sum(1 for l in internal + external if l["text"].lower() in ("click here", "en savoir plus", "voir", "ici"))
        if generic > 0:
            self._add_issue("warning", "links", f"{generic} links with generic anchor text", "Use descriptive anchor text instead of 'click here'")

        return {"internal": len(internal), "external": len(external), "total": len(links)}

    def analyze_opengraph(self):
        og = {}
        for meta in self.soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            og[meta["property"]] = meta.get("content", "")

        required = ["og:title", "og:description", "og:image", "og:url"]
        missing = [r for r in required if r not in og]
        if missing:
            self._add_issue("warning", "og", f"Missing OG tags: {', '.join(missing)}", "Add complete OpenGraph tags for social sharing")
        else:
            self._add_pass("og", "All required OpenGraph tags present")
        return og

    def analyze_canonical(self):
        canonical = self.soup.find("link", rel="canonical")
        if not canonical or not canonical.get("href"):
            self._add_issue("warning", "seo", "No canonical tag found", "Add <link rel='canonical'> to prevent duplicate content")
        else:
            self._add_pass("seo", f"Canonical tag: {canonical['href'][:60]}")
        return canonical.get("href") if canonical else None

    def analyze_schema(self):
        scripts = self.soup.find_all("script", type="application/ld+json")
        if not scripts:
            self._add_issue("warning", "schema", "No schema markup (JSON-LD) found", "Add structured data: Product, FAQ, Breadcrumb, Organization")
        else:
            types = set()
            for script in scripts:
                try:
                    data = json.loads(script.string or "{}")
                    if isinstance(data, dict):
                        types.add(data.get("@type", ""))
                    elif isinstance(data, list):
                        for item in data:
                            types.add(item.get("@type", ""))
                except (json.JSONDecodeError, TypeError):
                    pass
            self._add_pass("schema", f"Schema types found: {', '.join(types)}")
            for critical_type in ["Product", "Organization", "LocalBusiness"]:
                if critical_type not in types:
                    self._add_issue("info", "schema", f"Consider adding {critical_type} schema")
        return types

    def analyze_viewport(self):
        viewport = self.soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            self._add_issue("error", "mobile", "No viewport meta tag", "Add <meta name='viewport' content='width=device-width'>")
        else:
            content = viewport.get("content", "")
            if "width=device-width" in content:
                self._add_pass("mobile", "Viewport set correctly")
            else:
                self._add_issue("warning", "mobile", f"Viewport may be non-standard: {content}")

    def analyze_robots(self):
        robots = self.soup.find("meta", attrs={"name": "robots"})
        if robots:
            content = robots.get("content", "")
            if "noindex" in content:
                self._add_issue("error", "seo", "Page has noindex directive!", "Remove noindex if page should rank in search")
            if "nofollow" in content:
                self._add_issue("warning", "seo", "Page has nofollow directive", "Check if intentional — affects link equity")

    def analyze_tracking(self):
        tracking_scripts = {
            "google_analytics": "gtag|google-analytics|ga.js|analytics.js",
            "google_tag_manager": "googletagmanager|gtm-",
            "facebook_pixel": "facebook.*fbevents|connect.facebook",
            "hotjar": "hotjar",
            "tiktok": "tiktok.*pixel",
            "hubspot": "js.hs-scripts|hubspot",
            "google_ads": "googleads|doubleclick|gclid",
        }
        found = []
        for name, pattern in tracking_scripts.items():
            if re.search(pattern, self.html, re.IGNORECASE):
                found.append(name)
        return found

    def analyze_performance_indicators(self):
        indicators = {}
        # Check for render-blocking resources
        css_count = len(self.soup.find_all("link", rel="stylesheet"))
        indicators["css_files"] = css_count
        if css_count > 5:
            self._add_issue("warning", "performance", f"{css_count} CSS files may impact load time", "Combine CSS files, consider critical CSS inlining")

        # Check for inline styles
        inline_styles = len(self.soup.find_all(style=True))
        indicators["inline_styles"] = inline_styles

        # Check for large images (by URL patterns suggesting uncompressed)
        large_img_patterns = [".png", ".bmp", ".tiff"]
        images = self.soup.find_all("img", src=True)
        uncompressed = sum(1 for img in images if any(img["src"].lower().endswith(ext) for ext in large_img_patterns))
        if uncompressed > 0:
            self._add_issue("warning", "performance", f"{uncompressed} images may be uncompressed formats", "Convert to WebP/AVIF for better compression")

        # Check for defer/async on scripts
        scripts = self.soup.find_all("script", src=True)
        deferred = sum(1 for s in scripts if s.get("defer") or s.get("async"))
        if scripts and deferred == 0:
            self._add_issue("warning", "performance", "No scripts use defer or async", "Add defer/async to non-critical scripts")
        elif deferred > 0:
            self._add_pass("performance", f"{deferred}/{len(scripts)} scripts use defer/async")

        return indicators

    def generate_content_analysis(self):
        # Remove script/style tags
        for tag in self.soup(["script", "style", "noscript"]):
            tag.decompose()
        text = self.soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        # Readability (simple metrics)
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = word_count / max(len(sentences), 1)

        # Keyword density
        common = Counter(w.lower() for w in words if len(w) > 3)
        top_keywords = common.most_common(20)

        return {
            "word_count": word_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "top_keywords": [(w, c) for w, c in top_keywords[:10]],
        }

    def run_full_audit(self):
        print(f"\n🔍 Analyzing: {self.url}\n{'='*60}")
        try:
            self.fetch()
        except Exception as e:
            print(f"❌ Failed to fetch page: {e}")
            return

        self.analyze_title()
        self.analyze_meta_description()
        self.analyze_headings()
        self.analyze_images()
        self.analyze_links()
        self.analyze_opengraph()
        self.analyze_canonical()
        self.analyze_schema()
        self.analyze_viewport()
        self.analyze_robots()
        tracking = self.analyze_tracking()
        performance = self.analyze_performance_indicators()
        content = self.generate_content_analysis()

        # Summary
        errors = [i for i in self.issues if i["severity"] == "error"]
        warnings_all = [i for i in self.issues if i["severity"] == "warning"] + self.warnings
        infos = [i for i in self.issues if i["severity"] == "info"]

        print(f"\n📊 RESULTS for {urlparse(self.url).netloc}{urlparse(self.url).path}")
        print(f"{'─'*60}")
        print(f"  ✅ Passed:   {len(self.passes)}")
        print(f"  ❌ Errors:   {len(errors)}")
        print(f"  ⚠️  Warnings:  {len(warnings_all)}")
        print(f"  ℹ️  Info:      {len(infos)}")
        print(f"  📝 Word count: {content['word_count']}")
        print(f"  📖 Avg sentence: {content['avg_sentence_length']} words")

        if tracking:
            print(f"  📊 Tracking: {', '.join(tracking)}")

        if errors:
            print(f"\n❌ ERRORS (must fix):")
            for e in errors:
                print(f"  • [{e['category']}] {e['message']}")
                if "recommendation" in e:
                    print(f"    → {e['recommendation']}")

        if warnings_all:
            print(f"\n⚠️  WARNINGS:")
            for w in warnings_all:
                cat = w.get("category", w.get("severity", ""))
                print(f"  • [{cat}] {w['message']}")
                if "recommendation" in w:
                    print(f"    → {w['recommendation']}")

        if infos:
            print(f"\nℹ️  SUGGESTIONS:")
            for i in infos:
                print(f"  • {i['message']}")

        print(f"\n✅ PASSED CHECKS:")
        for p in self.passes:
            print(f"  • [{p['category']}] {p['message']}")

        # Score
        total_checks = len(self.passes) + len(errors) + len(warnings_all)
        if total_checks > 0:
            score = (len(self.passes) * 2 - len(errors) * 3 - len(warnings_all) * 1) / (total_checks * 2) * 100
            score = max(0, min(100, score))
            grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"
            print(f"\n📈 SEO SCORE: {score:.0f}/100 (Grade: {grade})")

        print(f"\n{'='*60}")

        return {
            "url": self.url,
            "score": round(score, 1) if total_checks > 0 else 0,
            "grade": grade if total_checks > 0 else "N/A",
            "errors": errors,
            "warnings": warnings_all,
            "passes": self.passes,
            "content": content,
            "tracking": tracking,
            "performance": performance,
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_page.py <url>")
        print("\nExample: python analyze_page.py https://sklubs.fr")
        print("Or: python analyze_page.py https://bags.sklubs.fr")
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    analyzer = SEOAnalyzer(url)
    result = analyzer.run_full_audit()

    if "--json" in sys.argv:
        print(f"\n--- JSON OUTPUT ---")
        print(json.dumps(result, indent=2, default=str))
