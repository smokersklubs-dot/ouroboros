#!/usr/bin/env python3
"""
social_calendar.py — Génération Calendrier Réseaux Sociaux
Absorbed from OpenClaw ai-marketing-claude → Ouroboros
Usage: python social_calendar.py --platform instagram --days 30

Génère un calendrier éditorial optimisé par plateforme
pour les configurateurs SKLUBS (bags, jar, tote-bag, pins, carte de visite, vêtements, stickers).
"""

import json
import sys
import random
from datetime import datetime, timedelta

class SocialCalendarGenerator:
    PRODUCTS = [
        {"name": "Sacs personnalisés", "url": "bags.sklubs.fr", "emoji": "👜"},
        {"name": "Bocaux personnalisés", "url": "jar.sklubs.fr", "emoji": "🏺"},
        {"name": "Tote bags personnalisés", "url": "tote-bag.sklubs.fr", "emoji": "🛍️"},
        {"name": "Pins personnalisés", "url": "pins.sklubs.fr", "emoji": "📌"},
        {"name": "Cartes de visite", "url": "carte-de-visite.sklubs.fr", "emoji": "💳"},
        {"name": "Vêtements personnalisés", "url": "vetements.sklubs.fr", "emoji": "👕"},
        {"name": "Stickers personnalisés", "url": "sticker.sklubs.fr", "emoji": "🏷️"},
    ]

    CONTENT_PILLARS = {
        "instagram": {
            "post": ["product_showcase", "behind_scenes", "user_generated", "tutorial", "lifestyle", "meme"],
            "stories": ["poll", "question", "countdown", "link_sticker", "before_after"],
            "reels": ["process_video", "transformation", "unboxing", "how_to", "trending"],
        },
        "facebook": {
            "post": ["promotion", "testimonial", "event", "blog_share", "community"],
        },
        "tiktok": {
            "post": ["trend_dance", "product_reveal", "satisfying_design", "storytime", "duet"],
        },
        "linkedin": {
            "post": ["b2b_case_study", "company_update", "industry_tip", "partnership"],
        },
        "twitter": {
            "post": ["tip", "thread", "poll", "product_tip", "industry_comment"],
        },
    }

    POST_TEMPLATES = {
        "product_showcase": {
            "caption": [
                "✨ {emoji} {product} — Personnalisez le vôtre en quelques clics !\n\n🎨 Des milliers de combinaisons possibles\n📦 Livraison rapide\n💰 Prix imbattables\n\n👉 {url}",
                "🔥 Le hit du moment : {emoji} {product}\n\nPersonnalisez avec vos couleurs, votre logo, votre design.\n\nCréez maintenant : {url}",
                "🎁 Idéal comme cadeau : {emoji} {product} personnalisé\n\nFaites plaisir avec un produit unique.\n\n{url}",
            ],
            "hashtags": ["#personnalisation", "#custommade", "#cadeauoriginal", "#sklubs", "#madeinfrance"],
        },
        "behind_scenes": {
            "caption": [
                "🏭 Dans les coulisses de SKLUBS\n\nVoici comment votre {emoji} {product} prend vie...\n\nQualité + personnalisation à tous les niveaux.\n\nVoir le configurateur : {url}",
            ],
            "hashtags": ["#coulisses", "#production", "#savoirfaire", "#qualité"],
        },
        "user_generated": {
            "caption": [
                "📸 Merci @{client} pour ce superbe {emoji} {product} !\n\nPartagez vos créations avec #SklubsCustom\n\nCréez le vôtre : {url}",
            ],
            "hashtags": ["#ugc", "#clientheureux", "#sklubscustom", "#communauté"],
        },
        "tutorial": {
            "caption": [
                "📝 TUTO : Comment créer votre {emoji} {product} en 3 étapes\n\n1️⃣ Choisissez votre modèle\n2️⃣ Personnalisez (couleur, texte, image)\n3️⃣ Commandez !\n\nC'est aussi simple que ça → {url}",
            ],
            "hashtags": ["#tuto", "#commentfaire", "#guide", "#diy"],
        },
        "lifestyle": {
            "caption": [
                "☕ Lundi matin avec mon {emoji} {product} perso\n\nParce que chaque jour mérite un peu de style.\n\n{url}",
            ],
            "hashtags": ["#lifestyle", "#mood", "#personnalisé", "#quotidien"],
        },
        "meme": {
            "caption": [
                "😂 Quand tu reçois ton {emoji} {product} custom et que tu te rends compte que TOUT LE MONDE veut le même...\n\n{url}",
            ],
            "hashtags": ["#meme", "#humour", "#drôle", "#sklubs"],
        },
        "promotion": {
            "caption": [
                "🚨 OFFRE LIMITÉE !\n\n-20% sur tous les {emoji} {product} cette semaine\n\n⏰ Code : SKLUBS20\n\n{url}",
            ],
            "hashtags": ["#promotion", "#offre", "#reduction", "#bonplan"],
        },
        "testimonial": {
            "caption": [
                "💬 \"J'ai commandé des {product} pour mon entreprise. La qualité est top et mes clients adorent !\" — {client}\n\nRejoignez les {nombre} clients satisfaits → {url}",
            ],
            "hashtags": ["#avisclient", "#témoignage", "#confiance", "#qualité"],
        },
        "process_video": {
            "caption": [
                "🎬 Regardez ce {emoji} {product} prendre vie de A à Z ✨\n\nLa magie de la personnalisation.\n\nCréez le vôtre : {url}",
            ],
            "hashtags": ["#reels", "#process", "#satisfaisant", "#asMR"],
        },
        "unboxing": {
            "caption": [
                "📦 UNBOXING du {emoji} {product} SKLUBS\n\nPremière impression : la qualité est dingue 😍\n\nTestez le configurateur : {url}",
            ],
            "hashtags": ["#unboxing", "#réception", "#packaging", "#qualité"],
        },
        "b2b_case_study": {
            "caption": [
                "📊 Comment {entreprise} a renforcé son branding avec nos {emoji} {product} personnalisés\n\n+{pourcentage}% de visibilité auprès de leurs clients.\n\nDemandez un devis : {url}",
            ],
            "hashtags": ["#B2B", "#branding", "#entreprise", "#marketing"],
        },
        "thread": {
            "caption": [
                "🧵 Pourquoi la personnalisation est l'avenir du marketing (et comment SKLUBS s'y prépare)\n\n1/ La personnalisation augmente l'engagement de +40%\n2/ Les produits custom ont +35% de taux de rétention\n3/ ...",
            ],
            "hashtags": ["#thread", "#personnalisation", "#marketing"],
        },
    }

    OPTIMAL_POSTING_TIMES = {
        "instagram": {
            "Monday": ["07:00", "12:00", "19:00"],
            "Tuesday": ["08:00", "12:00", "20:00"],
            "Wednesday": ["08:00", "12:00", "19:00"],
            "Thursday": ["09:00", "12:00", "20:00"],
            "Friday": ["09:00", "12:00", "17:00"],
            "Saturday": ["10:00", "14:00", "19:00"],
            "Sunday": ["10:00", "15:00", "20:00"],
        },
        "facebook": {
            "Monday": ["13:00"],
            "Tuesday": ["13:00"],
            "Wednesday": ["13:00"],
            "Thursday": ["13:00"],
            "Friday": ["12:00"],
            "Saturday": ["12:00"],
            "Sunday": ["12:00"],
        },
        "tiktok": {
            "Monday": ["19:00"],
            "Tuesday": ["18:00"],
            "Wednesday": ["19:00"],
            "Thursday": ["19:00"],
            "Friday": ["17:00"],
            "Saturday": ["14:00"],
            "Sunday": ["16:00"],
        },
    }

    def __init__(self, platform="instagram", days=30, posts_per_day=1):
        self.platform = platform
        self.days = days
        self.posts_per_day = posts_per_day
        self.calendar = []

    def generate(self):
        pillar_config = self.CONTENT_PILLARS.get(self.platform, self.CONTENT_PILLARS["instagram"])
        post_types = pillar_config.get("post", list(self.POST_TEMPLATES.keys()))

        start_date = datetime.now()
        
        for day_offset in range(self.days):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            
            for post_num in range(self.posts_per_day):
                post_type = post_types[(day_offset * self.posts_per_day + post_num) % len(post_types)]
                product = self.PRODUCTS[day_offset % len(self.PRODUCTS)]
                
                template = self.POST_TEMPLATES.get(post_type, {
                    "caption": ["Post for {emoji} {product} → {url}"],
                    "hashtags": ["#sklubs"]
                })
                
                caption = random.choice(template["caption"]).format(
                    emoji=product["emoji"],
                    product=product["name"],
                    url=product["url"],
                    client="Client",
                    nombre="500+",
                    entreprise="Entreprise X",
                    pourcentage="40",
                )
                
                hashtags = template.get("hashtags", [])
                full_text = caption + "\n\n" + " ".join(hashtags)
                
                times = self.OPTIMAL_POSTING_TIMES.get(self.platform, self.OPTIMAL_POSTING_TIMES["instagram"])
                post_time = times.get(day_name, ["12:00"])[min(post_num, len(times.get(day_name, ["12:00"])) - 1)]
                
                post = {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "time": post_time,
                    "platform": self.platform,
                    "type": post_type,
                    "product": product["name"],
                    "product_url": product["url"],
                    "caption": caption,
                    "full_post": full_text,
                    "hashtags": hashtags,
                }
                self.calendar.append(post)

        return self.calendar

    def export_json(self):
        return json.dumps(self.calendar, indent=2, ensure_ascii=False)

    def export_markdown(self):
        lines = [
            f"# 📅 Calendrier Réseaux Sociaux — SKLUBS",
            f"## Plateforme: {self.platform.title()}",
            f"## Période: {self.days} jours",
            f"## Posts: {len(self.calendar)}\n"
        ]
        current_date = None
        for post in self.calendar:
            if post["date"] != current_date:
                current_date = post["date"]
                lines.append(f"\n### 📆 {current_date} ({post['day']})")
            lines.append(f"- **{post['time']}** — {post['type'].upper()} | {post['emoji']} {post['product']}")
            lines.append(f"  - Post: {post['caption'][:100]}...")
            lines.append(f"  - Hashtags: {' '.join(post['hashtags'])}")
        return "\n".join(lines)

    def export_csv(self):
        lines = ["date,day,time,platform,type,product,caption,hashtags"]
        for post in self.calendar:
            caption_escaped = post["caption"].replace('"', '""')
            lines.append(f'{post["date"]},{post["day"]},{post["time"]},{post["platform"]},{post["type"]},\"{post["product"]}\",\"{caption_escaped}\",\"{chr(32).join(post["hashtags"])}\"')
        return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Générer calendrier réseaux sociaux SKLUBS")
    parser.add_argument("--platform", default="instagram", 
                       choices=["instagram", "facebook", "tiktok", "linkedin", "twitter"],
                       help="Plateforme cible")
    parser.add_argument("--days", type=int, default=30, help="Nombre de jours")
    parser.add_argument("--posts-per-day", type=int, default=1, help="Posts par jour")
    parser.add_argument("--format", default="markdown",
                       choices=["markdown", "json", "csv"], help="Format de sortie")
    args = parser.parse_args()

    gen = SocialCalendarGenerator(
        platform=args.platform,
        days=args.days,
        posts_per_day=args.posts_per_day
    )
    gen.generate()

    if args.format == "json":
        print(gen.export_json())
    elif args.format == "csv":
        print(gen.export_csv())
    else:
        print(gen.export_markdown())
