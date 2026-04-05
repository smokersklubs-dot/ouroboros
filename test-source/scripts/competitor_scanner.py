#!/usr/bin/env python3
"""
competitor_scanner.py — Analyse Concurrentielle Automatisée
Absorbed from OpenClaw ai-marketing-claude → Ouroboros
Usage: python competitor_scanner.py <url1> [url2] [url3] ...

Compare les concurrents de SKLUBS sur :
- SEO on-page (title, meta, headings, mots-clés)
- Structure de prix (si détectable)
- Fonctionnalités offertes
- Social proof (témoignages, logos)
- Vitesse perçue (taille page, ressources)
"""

import json
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Requirement: pip install requests")
    sys.exit(1)


class CompetitorScanner:
    def __init__(self, urls):
        self.urls = urls
        self.results = {}

    def fetch_page(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return resp, soup
        except Exception as e:
            print(f"  ❌ Failed to fetch {url}: {e}")
            return None, None

    def extract_pricing_info(self, soup):
        """Essaie de détecter des indications de prix."""
        text = soup.get_text()
        prices = []
        import re
        # Euro prices
        price_patterns = re.findall(r'(\d+[,\.]?\d{0,2})\s*€?', text)
        relevant = []
        for p in price_patterns:
            try:
                val = float(p.replace(",", "."))
                if 1 < val < 10000:  # Filtrer les prix raisonnables
                    relevant.append(val)
            except ValueError:
                pass
        return sorted(set(relevant))[:10]

    def extract_ctas(self, soup):
        """Extrait les boutons/appels à l'action."""
        ctas = []
        for btn in soup.find_all(["button", "a"]):
            text = btn.get_text(strip=True).lower()
            if any(kw in text for kw in [
                "commander", "ajouter", "personnaliser", "configurer",
                "commencer", "démarrer", "acheter", "devis", "contact",
                "command", "add to cart", "customize"
            ]):
                ctas.append(text)
        return ctas

    def extract_contact_info(self, soup):
        """Extrait les infos de contact."""
        text = soup.get_text()
        contacts = {
            "phone": [],
            "email": [],
            "address": []
        }
        import re
        phones = re.findall(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', text)
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        contacts["phone"] = phones[:3]
        contacts["email"] = emails[:3]
        return contacts

    def analyze_social_proof(self, soup):
        """Détecte les éléments de preuve sociale."""
        text = soup.get_text().lower()
        proof = {}
        if any(w in text for w in ["témoignage", "testimonial", "avis client", "customer review"]):
            proof["has_testimonials"] = True
        if any(w in text for w in ["nos clients", "our clients", "ils nous font confiance"]):
            proof["has_client_logos"] = True
        if any(w in text for w in ["note", "rating", "étoile", "star"]):
            proof["has_ratings"] = True
        if any(w in text for w in ["+de ", "+ de ", "plus de ", "over "]):
            proof["has_statistics"] = True
        proof["trust_keywords"] = sum(1 for w in ["garantie", "warranty", "satisfait", "sécurité", "sécurité"] if w in text)
        return proof

    def analyze_page(self, resp, soup):
        if not soup:
            return None

        # Meta
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content", "") if meta_desc else ""

        # Content
        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        # Headings
        headings = {}
        for level in range(1, 4):
            tags = soup.find_all(f"h{level}")
            headings[f"h{level}"] = [t.get_text(strip=True) for t in tags]

        # Performance
        page_size_kb = len(resp.content) / 1024
        resource_count = len(soup.find_all(["img", "script", "link", "style"]))

        # Images
        images = soup.find_all("img")
        images_with_alt = sum(1 for img in images if img.get("alt"))

        # Links
        links = soup.find_all("a", href=True)
        internal_links = sum(1 for l in links if urlparse(l["href"]).netloc == urlparse(resp.url).netloc)

        return {
            "url": resp.url,
            "title": title,
            "title_length": len(title),
            "meta_description": description,
            "meta_description_length": len(description),
            "word_count": word_count,
            "page_size_kb": round(page_size_kb, 1),
            "resource_count": resource_count,
            "headings": headings,
            "total_images": len(images),
            "images_with_alt": images_with_alt,
            "total_links": len(links),
            "internal_links": internal_links,
            "external_links": len(links) - internal_links,
            "ctas": self.extract_ctas(soup),
            "pricing_hints": self.extract_pricing_info(soup),
            "social_proof": self.analyze_social_proof(soup),
            "contact": self.extract_contact_info(soup),
        }

    def run(self):
        print(f"\n🔍 Analyse concurrentielle de {len(self.urls)} sites")
        print(f"{'='*70}")

        for url in self.urls:
            print(f"\n📄 Analysing: {url}")
            resp, soup = self.fetch_page(url)
            result = self.analyze_page(resp, soup)
            if result:
                self.results[url] = result
                print(f"  ✅ Title: {result['title'][:60]}")
                print(f"  ✅ Meta: {result['meta_description'][:80] or '❌ Missing'}")
                print(f"  ✅ Content: {result['word_count']} words, {result['page_size_kb']}KB")
                print(f"  ✅ CTAs: {len(result['ctas'])}")
                if result['ctas']:
                    for c in result['ctas'][:3]:
                        print(f"    → {c}")
                if result['pricing_hints']:
                    print(f"  💰 Prix détectés: {result['pricing_hints'][:5]}")
                proof = result['social_proof']
                proof_count = sum(1 for v in proof.values() if v and v != 0)
                print(f"  🏆 Social proof elements: {proof_count}")

        return self.results

    def generate_report(self):
        if not self.results:
            return "No data to compare."

        print(f"\n{'='*70}")
        print("📊 RAPPORT COMPARATIF")
        print(f"{'='*70}")

        # Comparison table
        print(f"\n{'Critère':<25} | " + " | ".join(f"{urlparse(u).netloc[:15]:<15}" for u in self.results))
        print(f"{'-'*25}-+-{'-'*17*-1}" if False else f"{'─'*25}-┼-{'─'*(17*len(self.results))}")

        metrics = [
            ("Titre", lambda r: r['title'][:30]),
            ("Mots", lambda r: str(r['word_count'])),
            ("Taille page", lambda r: f"{r['page_size_kb']}KB"),
            ("Images", lambda r: f"{r['images_with_alt']}/{r['total_images']}"),
            ("Liens internes", lambda r: str(r['internal_links'])),
            ("CTAs", lambda r: str(len(r['ctas']))),
            ("Prix détectés", lambda r: str(len(r['pricing_hints']))),
        ]

        for label, getter in metrics:
            values = " | ".join(f"{getter(r):<15}" for r in self.results.values())
            print(f"{label:<25} | {values}")

        print(f"\n{'='*70}")
        return json.dumps(self.results, indent=2, default=str, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python competitor_scanner.py <url1> [url2] [url3] ...")
        print("\nExample: python competitor_scanner.py "
              "https://vistaprint.fr https://flyeralarm.com https://4over.com")
        sys.exit(1)

    scanner = CompetitorScanner(sys.argv[1:])
    scanner.run()
    scanner.generate_report()
