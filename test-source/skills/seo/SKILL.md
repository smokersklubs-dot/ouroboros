# 🧠 SKILL: SEO MASTER

**Owner:** Ouroboros  
**Purpose:** Audit SEO, optimisation, et domination SERP pour les pages SKLUBS  
**Scope:** 7 configurateurs de produits + site principal  
**Updated:** 2026-04-05

---

## 1. PRINCIPES FONDAMENTAUX

Le SEO n'est pas une checkbox — c'est une discipline d'ingénierie du contenu. Chaque page SKLUBS doit être une arme de guerre pour son mot-clé cible.

### Hiérarchie d'importance :
1. **Intent match** — La page correspond-elle à ce que Google veut montrer ?
2. **Content quality** — E-E-A-T : Experience, Expertise, Authority, Trust
3. **Technical foundation** — Performance, crawlability, indexability
4. **Off-page signals** — Backlinks, mentions, authority

---

## 2. AUDIT SEO (10-STEP METHODOLOGY)

### Step 1: Quick Scan
- Title tag (50-60 chars)
- Meta description (150-160 chars)
- Un seul H1 avec keyword
- Canonical tag présent
- Pas de noindex/nofollow

### Step 2: Content Depth Analysis
- **Minimum viable word count**: 800+ words pour pages produit, 1500+ pour pages pilier
- **Keyword placement**: Dans les 100 premiers mots, H1, H2, meta description, URL
- **Density**: 1-2% pour le keyword principal, <1% pour secondary
- **Semantic field**: Utiliser des mots-clés LSI et synonymes

### Step 3: Keyword Mapping par Configurateur
| URL | Keyword Primary | Keywords Secondary |
|-----|----------------|-------------------|
| bags.sklubs.fr | sac personnalisé | bag floqué, sac publicitaire, tote bag entreprise |
| jar.sklubs.fr | bocal personnalisé | pot personnalisé, jar personnalisable, packaging sur mesure |
| tote-bag.sklubs.fr | tote bag personnalisé | sac en coton custom, tote pas cher, tote bio personnalisé |
| pins.sklubs.fr | pins personnalisé | badge personnalisé, épingles sur mesure, pins publicitaires |
| carte-de-visite.sklubs.fr | carte de visite | cartes professionnelles, business cards, cartes imprimées |
| vetements.sklubs.fr | vêtement personnalisé | t-shirt personnalisé, polo personnalisé, textile pro |
| sticker.sklubs.fr | sticker personnalisé | autocollant sur mesure, stickers publicitaires, étiquettes |
| sklubs.fr | personnalisation produits | objets personnalisés, goodie custom, marketing personnalisé |

### Step 4: Technical SEO Checklist
- Page speed: LCP < 2.5s, CLS < 0.1, INP < 200ms
- Core Web Vitals pass > 90%
- robots.txt: ne pas bloquer CSS/JS
- sitemap.xml: toutes les configurateurs indexés
- Hreflang si multilingue
- SSL/TLS actif
- HTTP/2 ou HTTP/3

### Step 5: Schema Markup Obligatoire
Chaque configurateur de produit MUST avoir :
- **Product Schema**: name, description, image, offers, aggregateRating
- **BreadcrumbList**: Accueil > Catégorie > Produit
- **FAQPage**: 3-5 questions fréquentes

Le site principal doit avoir :
- **Organization Schema**: name, url, logo, social profiles
- **LocalBusiness** si applicable (adresse, téléphone, heures)

### Step 6: Featured Snippet Strategy
Pour chaque keyword principal, structurer du contenu qui peut voler le snippet :
- **Paragraph**: 40-60 mots, réponse directe après une question en H2
- **List**: steps ou éléments dans ol/ul
- **Table**: HTML avec headers clairs
- **Video**: avec schema VideoObject

### Step 7: Internal Linking Architecture
```
sklubs.fr (homepage)
├── Configurateurs (7 pages)
│   ├── bags.sklubs.fr → cross-link vers vetements, tote-bag
│   ├── tote-bag.sklubs.fr → cross-link vers bags, stickers
│   └── ...
├── Blog (pilier pages + cluster)
│   ├── Guide personnalisation [pilier]
│   │   ├── Comment personnaliser un sac [cluster]
│   │   ├── Idées cadeaux personnalisés [cluster]
│   │   └── ...
│   └── Marketing personnalisé [pilier]
│       ├── ROI des goodies [cluster]
│       └── ...
└── À propos / Contact / FAQ
```

### Step 8: Competitor Gap Analysis
1. Extraire les keywords des 3 premier concurrents
2. Identifier les gaps (keywords qu'ils rank mais pas SKLUBS)
3. Créer du contenu pour combler les gaps
4. Optimiser les pages existantes avec des keywords manquantes

### Step 9: Local SEO (si applicable)
- Google Business Profile optimisé
- NAP cohérent (Name, Address, Phone)
- Local citations sur annuaires FR
- Reviews management

### Step 10: Monitoring & KPIs
- **Organic traffic**: +15%/mois minimum
- **Keyword rankings**: Top 10 pour keywords cible
- **CTR**: > 3% sur SERP
- **Bounce rate**: < 60% pour entrées organiques
- **Pages indexées**: 100% des configurateurs + contenu

---

## 3. ON-PAGE OPTIMIZATION FRAMEWORK

### Title Tag Formula (E-commerce)
```
[Produit] personnalisé en ligne - [Avantage] | SKLUBS
Ex: Sac personnalisé en ligne - Créez votre design unique | SKLUBS
```

### Meta Description Formula
```
[Action verb] votre [produit] personnalisé [avantage unique]. ✓ [Benefit 1] ✓ [Benefit 2] ✓ [Benefit 3]. Commandez maintenant sur SKLUBS.
Ex: Créez votre sac personnalisé en ligne. ✓ Design unique ✓ Livraison rapide ✓ Prix imbattable. Commandez maintenant sur SKLUBS.
```

### H1 Formula
```
Personnalisez votre [Nom du Produit] en ligne
```

### URL Structure
```
sklubs.fr/configurateur-de-sacs-personnalises
→ Préférer: bags.sklubs.fr (sous-domaine) ou sklubs.fr/sacs-personnalises
→ Under 75 chars, hyphens, lowercase, no params
```

### Image SEO
- Nom du fichier: `sac-personnalise-noir-cuir-sklubs.jpg` (pas `IMG_001.jpg`)
- Alt text: descriptif avec keyword naturel
- Format: WebP avec fallback JPEG
- Max 200KB par image (optimisé)
- Lazy loading pour below-fold

---

## 4. CONTENT OPTIMIZATION

### Product Page Content Structure (Ideal)
1. **Hero** (H1 + Configurator embed + CTA)
2. **Benefits** (3-4 cards with icons)
3. **How it works** (3 steps, visual)
4. **Gallery** (real customer creations, UGC)
5. **Specifications** (table: materials, sizes, quantities)
6. **Testimonials** (3-5 reviews with stars)
7. **FAQ** (5-8 questions, schema markup)
8. **Related Products** (cross-link to other configurators)

### Blog Content Requirements
- **Minimum**: 1500 words
- **Structure**: H1 → 3-5 H2 → H3 sous chaque H2
- **Internal links**: 5-10 per post
- **Images**: 3-5 avec alt text
- **CTA**: Liens vers configurateur dans premier et dernier paragraphe
- **Originality**: Pas de contenu AI non édité — ajouter expertise personnelle

---

## 5. TECHNICAL SEO AUTOMATION

### Scripts disponibles :
- `analyze_page.py` — Audit SEO complet d'une URL
  ```bash
  python analyze_page.py https://bags.sklubs.fr
  python analyze_page.py https://bags.sklubs.fr --json
  ```

### Checkpoints réguliers :
1. **Crawl mensuel** de toutes les URLs → détecter 404/5xx
2. **Vérification des balises** (title, meta, canonical) sur chaque page
3. **Performance** : GTmetrix/PageSpeed API checks
4. **Indexation** : `site:sklubs.fr` pour vérifier pages indexées
5. **Backlinks** : suivi avec Ahrefs/Semrush API

---

## 6. QUICK REFERENCE: SEO SCORECARD

| Critère | Poids | Score Target |
|---------|-------|-------------|
| Title Tag | 10% | 10/10 |
| Meta Description | 10% | 10/10 |
| H1 & Headings | 10% | 10/10 |
| Content Quality | 15% | 8+/10 |
| Internal Links | 10% | 5-10/page |
| Image Optimization | 10% | Tous optimisés |
| Page Speed | 10% | LCP < 2.5s |
| Schema Markup | 10% | Product + FAQ |
| Mobile Friendliness | 5% | 100% |
| Canonical | 5% | Présent |
| URL Structure | 5% | Clean |

**Score minimum acceptable**: 80/100 pour chaque configurateur.
