# 🧠 SKILL: SOCIAL MEDIA STRATEGY

**Owner:** Ouroboros  
**Purpose:** Stratégie réseaux sociaux pour SKLUBS — Instagram, Facebook, TikTok, LinkedIn  
**Updated:** 2026-04-05

---

## 1. STRATÉGIE PAR PLATEFORME

### Instagram — L'Écrin Visuel
**Objectif**: Montrer la qualité et le processus créatif  
**Format principal**: Reels (60%), Carrousels (25%), Stories (15%)  
**Fréquence**: 5 posts/semaine + 3 stories/jour  

**Content Pillars:**
1. **Product Showcase** (30%) — Photos et vidéos de produits finis, unboxing
2. **Behind the Scenes** (20%) — Process de personnalisation, coulisses, impression
3. **User Generated Content** (20%) — Repost clients, témoignages visuels
4. **Tips & Tutorials** (15%) — Comment bien personnaliser, inspiration design
5. **Promotions** (10%) — Offres, codes promo, nouveautés
6. **Lifestyle/Meme** (5%) — Contenu humoristique, trending

**Optimisation SKLUBS:**
- Chaque configurateur = 1 post/semaine minimum
- Utiliser les configurateurs pour créer du contenu (screen record du processus)
- Stories avec sondages : "Quel design préférez-vous ? A ou B"
- Reels avec musique trending + overlay "Satisfying design process"
- Hashtags stratégiques : 5-8 par post, mix broad + niche

### Facebook — La Communauté
**Objectif**: Construire une communauté fidèle et générer du traffic  
**Format principal**: Posts longs, photos, événements  
**Fréquence**: 3 posts/semaine  

**Content Strategy:**
- Posts avec questions pour engager
- Partages d'articles blog avec commentaires
- Annonces de promotions (communauté = accès anticipé)
- Événements Facebook pour lancements
- Groupes Facebook : créer un groupe "Créatifs SKLUBS"

### TikTok — La Viralité
**Objectif**: Atteindre un jeune public et créer du contenu viral  
**Format principal**: Vidéos courtes (15-60s)  
**Fréquence**: 1-2 vidéos/jour  

**Content Ideas:**
1. **Satisfying process** — Time-lapse de création de designs
2. **Before/After** — Design brut vs produit fini
3. **Trend participation** — Sons tendance appliqués aux produits SKLUBS
4. **"POV"** — POV: Tu reçois tes stickers SKLUBS en livraison
5. **Behind the scenes** — L'impression en action
6. **Customer reactions** — Unboxing réels
7. **"3 reasons why"** — 3 raisons de personnaliser avec SKLUBS

### LinkedIn — Le B2B
**Objectif**: Capter les entreprises et professionnels  
**Format principal**: Posts texte + image, études de cas  
**Fréquence**: 2 posts/semaine  

**Content Strategy:**
- Études de cas B2B (ex: "Comment XYZ a augmenté sa visibilité de 40%")
- Conseils marketing pour les PME
- Données chiffrées sur le ROI des produits personnalisés
- Posts sur l'entrepreneuriat et le branding
- Partages d'événements professionnels

---

## 2. CALENDRIER TYPE (Semaine)

| Jour | Instagram | Facebook | TikTok | LinkedIn |
|------|-----------|----------|--------|----------|
| Lundi | Tuto Reel (bags) | Post communauté | Trend sound + produit | - |
| Mardi | Carrousel (tips) | - | Satisfying process | Conseil marketing B2B |
| Mercredi | UGC repost | Promotion | Before/After | - |
| Jeudi | Product showcase (jars) | Article blog | POV delivery | Étude de cas |
| Vendredi | Meme/Trending | Offre weekend | Trend + produit | - |
| Samedi | Lifestyle photo | - | Customer reaction | - |
| Dimanche | Story Q&A | Communauté | Compilation semaine | - |

---

## 3. ENGAGEMENT STRATEGY

### Règle des 15 minutes
Avant et après chaque post :
- 5 min : répondre aux commentaires sur vos posts
- 5 min : commenter les posts d'autres comptes (concurrents, clients, partenaires)
- 5 min : répondre aux DMs

### Community Management
- Répondre à TOUS les commentaires dans les 2h
- Répondre à TOUS les DMs dans les 4h
- Reposter le contenu client (UGC) avec crédit
- Créer des sondages/stories interactifs quotidiens

### Growth Hacks
1. **Collaborations**: Partenariats avec micro-influenceurs (1K-10K followers)
2. **Giveaways**: Concours "Tague 3 amis + follow pour gagner"
3. **Hashtag strategy**: 3 hashtags broad (1M+) + 3 niche (10K-100K) + 2 branded
4. **Cross-promotion**: Rediriger TikTok → Instagram → Site
5. **User challenges**: Challenge créatif avec hashtag dédié

---

## 4. HASHTAG STRATEGY

### Par Produit
| Produit | Hashtags |
|---------|----------|
| Sacs | #sacpersonnalisé #bagcustom #sacpub #goodieentreprise #sklubs |
| Bocaux | #bocalpersonnalisé #packagingsurmesure #cosmétiquebio #packagingdesign |
| Tote bags | #totebagpersonnalisé #totebagfr #sacenToile #ecofriendly #customtote |
| Pins | #pinspersonnalisé #badgesurmesure #pincollector #goodies |
| Cartes | #carteDeVisite #businesscard #printdesign #brandingpro |
| Vêtements | #vetementPersonnalisé #tshirtcustom #textilepro #uniformeentreprise |
| Stickers | #stickerpersonnalisé #autocollantcustom #stickersfr #packaging |

### Hashtags Branded
- #Sklubs (principal)
- #SklubsCustom (UGC)
- #SklubsCreation (contenu design)

---

## 5. METRICS & KPIs

### À tracker par plateforme
| Métrique | Cible Mensuelle |
|----------|----------------|
| Followers (Instagram) | +15% |
| Engagement rate (IG) | > 4% |
| Reach (TikTok) | > 100K |
| Video views (TikTok) | > 50K/post |
| CTR au site | > 2% |
| Cost per click (ads) | < €0.50 |
| Conversion từ social | > 3% |

### Outils recommandés
- **Planification**: Buffer ou Later
- **Analytics**: Native + UTM parameters
- **Design**: Canva templates + scripts social_calendar.py
- **Monitoring**: Mention ou Brand24 pour brand mentions

---

## 6. SCRIPT AUTOMATISÉ

Le script `social_calendar.py` génère automatiquement un calendrier éditorial :

```bash
# Calendrier Instagram 30 jours
python social_calendar.py --platform instagram --days 30

# Calendrier TikTok 14 jours, 2 posts/jour
python social_calendar.py --platform tiktok --days 14 --posts-per-day 2

# Export en JSON pour intégration
python social_calendar.py --platform facebook --format json

# Export CSV pour Google Sheets
python social_calendar.py --platform instagram --format csv
```

---

## 7. CRISIS MANAGEMENT

### Scénarios et réponses
| Situation | Action immédiate |
|-----------|-----------------|
| Commentaire négatif public | Répondre sous 30 min, proposer solution en DM |
| Produit défectueux signalé | Excuses + remplacement + crédit |
| Retard de livraison | Post transparent sur la situation + compensation |
| Fake news / rumeur | Réponse factuelle courte + preuve |
| Bad review | Jamais agressif — professionnalisme = confiance |
