#!/usr/bin/env python3
import requests
import time
import random
import re

TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

RECHERCHES = [
    {"nom": "iPhone 12", "mots_cles": "iphone 12", "modele": "12", "prix_min": 0, "prix_max": 80},
    {"nom": "iPhone 12 Pro", "mots_cles": "iphone 12 pro", "modele": "12 pro", "prix_min": 0, "prix_max": 100},
    {"nom": "iPhone 12 Pro Max", "mots_cles": "iphone 12 pro max", "modele": "12 pro max", "prix_min": 0, "prix_max": 120},
    {"nom": "iPhone 13", "mots_cles": "iphone 13", "modele": "13", "prix_min": 0, "prix_max": 130},
    {"nom": "iPhone 13 Pro", "mots_cles": "iphone 13 pro", "modele": "13 pro", "prix_min": 0, "prix_max": 150},
    {"nom": "iPhone 13 Pro Max", "mots_cles": "iphone 13 pro max", "modele": "13 pro max", "prix_min": 0, "prix_max": 170},
    {"nom": "iPhone 14", "mots_cles": "iphone 14", "modele": "14", "prix_min": 0, "prix_max": 160},
    {"nom": "iPhone 14 Pro", "mots_cles": "iphone 14 pro", "modele": "14 pro", "prix_min": 0, "prix_max": 200},
    {"nom": "iPhone 14 Pro Max", "mots_cles": "iphone 14 pro max", "modele": "14 pro max", "prix_min": 0, "prix_max": 230},
    {"nom": "iPhone 15", "mots_cles": "iphone 15", "modele": "15", "prix_min": 0, "prix_max": 250},
    {"nom": "iPhone 15 Pro", "mots_cles": "iphone 15 pro", "modele": "15 pro", "prix_min": 0, "prix_max": 320},
    {"nom": "iPhone 15 Pro Max", "mots_cles": "iphone 15 pro max", "modele": "15 pro max", "prix_min": 0, "prix_max": 380},
    {"nom": "iPhone 16", "mots_cles": "iphone 16", "modele": "16", "prix_min": 0, "prix_max": 300},
    {"nom": "iPhone 16 Pro", "mots_cles": "iphone 16 pro", "modele": "16 pro", "prix_min": 0, "prix_max": 400},
    {"nom": "iPhone 16 Pro Max", "mots_cles": "iphone 16 pro max", "modele": "16 pro max", "prix_min": 0, "prix_max": 500},
]

MOTS_CASSE = [
    "cass", "vitre", "ecran", "fissur", "bris", "crack",
    "hs", "abim", "rayur", "choc", "impact", "broken",
    "reparer", "defaut", "defectueux", "pour pieces", "reconditionne",
]

MOTS_ACCESSOIRES = [
    "coque", "housse", "etui", "bumper", "cover", "silicone",
    "tpu", "cuir", "portefeuille", "flip", "verre trempe",
    "film protecteur", "screen protector", "chargeur", "cable",
    "adaptateur", "ecouteurs", "airpods", "earpods", "casque",
    "batterie externe", "dummy", "factice", "maquette", "replica",
    "fake", "boite vide", "scatola", "box vide",
]

MOTS_SCAM = [
    "contacter en prive", "contacter moi", "whatsapp",
    "virement bancaire", "virement uniquement", "virement iban",
    "paiement via", "paypal ami", "western union",
    "carte cadeau", "iban uniquement", "contattatemi",
    "pari al nuovo", "perfetto stato", "in buone condizioni",
]

MODELES_INTERDITS = ["xr", "xs", "x ", "11", "se", " 8 ", " 7 ", " 6 "]

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
    m = modele.lower()
    if "pro max" in m:
        if "pro max" not in t:
            return False
        num = m.replace(" pro max", "")
        if f"iphone {num}" not in t and f"iphone{num}" not in t:
            return False
    elif "pro" in m:
        if "pro" not in t or "pro max" in t:
            return False
        num = m.replace(" pro", "")
        if f"iphone {num}" not in t and f"iphone{num}" not in t:
            return False
    else:
        if f"iphone {m}" not in t and f"iphone{m}" not in t:
            return False
        if "pro" in t:
            return False
    for mauvais in MODELES_INTERDITS:
        if mauvais in t:
            return False
    return True

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
            "per_page": 30
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
                print(f"🚫 {titre[:35]}")
                continue
            if est_accessoire(titre):
                print(f"🔧 {titre[:35]}")
                continue
            if not verifier_modele(titre, recherche["modele"]):
                print(f"❌ {titre[:35]}")
                continue
            if not est_casse(titre, description):
                print(f"⏭️ {titre[:35]}")
                continue

            msg = (
                f"🔥 <b>{recherche['nom']} trouvé!</b>\n"
                f"📱 {titre}\n"
                f"💰 {prix_valide:.2f}€\n"
                f"🔗 <a href='{url}'>VOIR SUR VINTED</a>"
            )
            if envoyer_telegram(msg):
                print(f"✅ {titre[:35]} — {prix_valide}€")
                matches += 1
        print(f"   {len(items)} scannés, {matches} matchs")
        return matches
    except Exception as e:
        print(f"Erreur {recherche['nom']}: {e}")
        return 0

def main():
    print("=" * 40)
    print("BOT VINTED V5")
    print("=" * 40)
    envoyer_telegram("🚀 Bot Vinted V5 démarré!")
    cycle = 1
    while True:
        print(f"\n📦 CYCLE #{cycle}")
        session = creer_session()
        for r in RECHERCHES:
            print(f"🔍 {r['nom']}")
            scraper(session, r)
            time.sleep(random.uniform(2, 4))
        print(f"⏳ Pause 30 sec...")
        cycle += 1
        time.sleep(30)

if __name__ == "__main__":
    main()
