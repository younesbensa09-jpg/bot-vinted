#!/usr/bin/env python3
import requests
import time
import random
import re

TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

RECHERCHES = [
    # 🎧 UNIQUEMENT LE SONY XM4 (Entre 40€ et 85€ max)
    {"nom": "Sony WH-1000XM4", "mots_cles": "sony wh-1000xm4", "modele": "xm4", "prix_min": 40, "prix_max": 85},
]

MOTS_CASSE = [
    "cass", "vitre", "ecran", "fissur", "bris", "crack",
    "hs", "abim", "rayur", "choc", "impact", "broken",
    "reparer", "defaut", "defectueux", "pour pieces", "reconditionne",
    "un côté ne marche plus", "mousse à changer", "fissuré"
]

MOTS_ACCESSOIRES = [
    "coque", "housse", "etui", "bumper", "cover", "silicone",
    "tpu", "cuir", "portefeuille", "flip", "verre trempe",
    "film protecteur", "screen protector", "chargeur", "cable",
    "adaptateur", "ecouteurs", "airpods", "earpods",
    "batterie externe", "dummy", "factice", "maquette", "replica",
    "fake", "boite vide", "scatola", "box vide", "boite seule", "packaging"
]

MOTS_SCAM = [
    "contacter en prive", "contacter moi", "whatsapp",
    "virement bancaire", "virement uniquement", "virement iban",
    "paiement via", "paypal ami", "western union",
    "carte cadeau", "iban uniquement", "contattatemi",
    "pari al nuovo", "perfetto stato", "in buone CONDITIONS",
    "copie", "fausse", "faux", "replique", "réplique"
]

annonces_vues = set()

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except:
        return False

def est_casse(titre, description=""):
    texte = (titre + " " + description).lower()
    return any(mot in texte for mot in MOTS_CASSE)

def est_scam(titre, description=""):
    texte = (titre + " " + description).lower()
    if re.search(r'\b\d{10}\b', texte):
        return True
    return any(mot in texte for mot in MOTS_SCAM)

def est_accessoire(titre):
    return any(mot in titre.lower() for mot in MOTS_ACCESSOIRES)

def verifier_modele(titre, modele):
    t = titre.lower()
    return "xm4" in t or "1000xm4" in t

def valider_prix(prix):
    try:
        if isinstance(prix, (int, float)):
            return float(prix)
        if isinstance(prix, str):
            p = re.sub(r'[^\d.,]', '', prix).replace(',', '.')
            return float(p)
    except:
        return None

def creer_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        ]),
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    return session

def scraper(session, recherche):
    try:
        session.get("https://www.vinted.fr", timeout=10)
        time.sleep(random.uniform(1, 3))
        params = {
            "search_text": recherche["mots_cles"],
            "price_from": recherche["prix_min"],
            "price_to": recherche["prix_max"],
            "order": "newest_first",
            "currency": "EUR",
            "per_page": 30,
            "status_ids[]": [1, 2, 6]  # Uniquement Neuf et Très bon état
        }

        r = session.get("https://www.vinted.fr/api/v2/catalog/items", params=params, timeout=15)
        if r.status_code != 200:
            print(f"Bloqué ({r.status_code})")
            return 0
            
        items = r.json().get('items', [])
        matches = 0
        for item in items:
            item_id = item.get('id')
            titre = item.get('title', '')
            description = item.get('description', '')
            prix_data = item.get('total_item_price', {})
            prix = prix_data.get('amount') if isinstance(prix_data, dict) else prix_data
            url = f"https://www.vinted.fr{item.get('path', '')}"

            if not item_id or item_id in annonces_vues:
                continue
            annonces_vues.add(item_id)

            prix_valide = valider_prix(prix)
            if not prix_valide:
                continue
            if est_scam(titre, description):
                print(f"🚫 Faux évité : {titre[:35]}")
                continue
            if est_accessoire(titre):
                print(f"🔧 Accessoire évité : {titre[:35]}")
                continue
            if not verifier_modele(titre, recherche["modele"]):
                print(f"❌ Mauvais modèle évité : {titre[:35]}")
                continue
            if est_casse(titre, description):
                print(f"⏭️ Cassé évité : {titre[:35]}")
                continue

            msg = (
                f"🔥 <b>{recherche['nom']} trouvé !</b>\n"
                f"🎧 {titre}\n"
                f"💰 {prix_valide:.2f}€\n"
                f"🔗 <a href='{url}'>VOIR SUR VINTED</a>"
            )
            if envoyer_telegram(msg):
                print(f"✅ Match : {titre[:35]} — {prix_valide}€")
                matches += 1
        print(f"   {len(items)} scannés, {matches} matchs")
        return matches
    except Exception as e:
        print(f"Erreur {recherche['nom']}: {e}")
        return 0

def main():
    print("=" * 40)
    print("BOT SONY XM4 EXCLUSIF")
    print("=" * 40)
    envoyer_telegram("🚀 Bot Chasseur Sony WH-1000XM4 démarré !")
    cycle = 1
    while True:
        print(f"\n📦 CYCLE #{cycle}")
        session = creer_session()
        for r in RECHERCHES:
            print(f"🔍 Scan en cours : {r['nom']}")
            scraper(session, r)
            time.sleep(random.uniform(2, 4))
        print(f"⏳ Pause 30 sec...")
        cycle += 1
        time.sleep(30)

if __name__ == "__main__":
    main()
