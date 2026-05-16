#!/usr/bin/env python3
import requests
import time
import random
import re
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

RECHERCHES = [
    {"nom": "iPhone 12", "mots_cles": "iphone 12 casse", "modele": "12", "prix_min": 45, "prix_max": 80},
    {"nom": "iPhone 12 Pro", "mots_cles": "iphone 12 pro casse", "modele": "12 pro", "prix_min": 60, "prix_max": 100},
    {"nom": "iPhone 12 Pro Max", "mots_cles": "iphone 12 pro max casse", "modele": "12 pro max", "prix_min": 70, "prix_max": 120},
    {"nom": "iPhone 13", "mots_cles": "iphone 13 casse", "modele": "13", "prix_min": 70, "prix_max": 130},
    {"nom": "iPhone 13 Pro", "mots_cles": "iphone 13 pro casse", "modele": "13 pro", "prix_min": 90, "prix_max": 150},
    {"nom": "iPhone 13 Pro Max", "mots_cles": "iphone 13 pro max casse", "modele": "13 pro max", "prix_min": 100, "prix_max": 170},
    {"nom": "iPhone 14", "mots_cles": "iphone 14 casse", "modele": "14", "prix_min": 90, "prix_max": 160},
    {"nom": "iPhone 14 Pro", "mots_cles": "iphone 14 pro casse", "modele": "14 pro", "prix_min": 120, "prix_max": 200},
    {"nom": "iPhone 14 Pro Max", "mots_cles": "iphone 14 pro max casse", "modele": "14 pro max", "prix_min": 140, "prix_max": 230},
    {"nom": "iPhone 15", "mots_cles": "iphone 15 casse", "modele": "15", "prix_min": 130, "prix_max": 250},
    {"nom": "iPhone 15 Pro", "mots_cles": "iphone 15 pro casse", "modele": "15 pro", "prix_min": 180, "prix_max": 320},
    {"nom": "iPhone 15 Pro Max", "mots_cles": "iphone 15 pro max casse", "modele": "15 pro max", "prix_min": 200, "prix_max": 380},
]

# Pièces détachées vendues SEULES — on veut pas ça
MOTS_PIECES_SEULES = [
    "ecran seul", "lcd seul", "dalle seule", "vitre seule",
    "chassis seul", "carcasse seule", "frame seul",
    "batterie seule", "back glass seul", "vitre arriere seule",
    "pour pieces", "vendu pour pieces", "hs pour pieces",
    "nappe seule", "flex seul", "connecteur seul",
    "camera seule", "objectif seul", "capteur seul",
    "bouton seul", "speaker seul", "micro seul",
    "lot de pieces", "kit reparation",
]

# Accessoires — on veut pas ça non plus
MOTS_ACCESSOIRES = [
    "coque", "housse", "etui", "bumper", "cover",
    "silicone", "plastique", "tpu", "cuir",
    "portefeuille", "flip", "wallet", "armor", "antichoc",
    "verre trempe", "film protecteur", "screen protector", "tempered",
    "chargeur", "cable", "adaptateur", "ecouteurs",
    "airpods", "earpods", "casque", "support voiture",
    "batterie externe", "powerbank",
    "dummy", "factice", "maquette", "replica", "fake", "copie", "clone",
    "boite vide", "box vide", "scatola", "boite seule", "carton vide",
    "outils", "tournevis",
]

# Scams
MOTS_SCAM = [
    "contacter en prive", "contacter en privé", "contacter moi",
    "whatsapp", "contactez moi", "appeler moi", "appelle moi",
    "virement bancaire", "virement uniquement", "virement iban",
    "paiement via", "paypal ami", "paypal friend",
    "western union", "carte cadeau", "gift card",
    "iban uniquement", "paypal ou virement",
    "ecrire en prive", "envoyer message",
    "in buone condizioni", "contattatemi", "informazione",
    "scatola", "nuova", "nuovo", "perfetto", "ottime",
    "condiciones", "contactar", "contattare",
    "telephone neuf en superbe", "neuf jamais utilise",
]

MODELES_INTERDITS = ["xr", "xs", "x ", "11", "se", "8 ", "7 ", "6 "]

annonces_vues = set()

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
        return response.status_code == 200
    except:
        return False

def est_un_scam(titre, description=""):
    texte = (titre + " " + description).lower()
    if re.search(r'\b\d{10}\b|\b\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}\b', texte):
        return True
    for mot in MOTS_SCAM:
        if mot in texte:
            return True
    return False

def est_une_piece_ou_accessoire(titre):
    if not titre:
        return True
    titre_lower = titre.lower()
    for mot in MOTS_PIECES_SEULES:
        if mot in titre_lower:
            return True
    for mot in MOTS_ACCESSOIRES:
        if mot in titre_lower:
            return True
    if "iphone" not in titre_lower:
        return True
    return False

def verifier_modele(titre, modele_recherche):
    titre_lower = titre.lower()
    modele_lower = modele_recherche.lower()
    if "pro max" in modele_lower:
        if "pro max" not in titre_lower:
            return False
        numero = modele_lower.replace(" pro max", "")
        if f"iphone {numero}" not in titre_lower and f"iphone{numero}" not in titre_lower:
            return False
    elif "pro" in modele_lower:
        if "pro" not in titre_lower or "pro max" in titre_lower:
            return False
        numero = modele_lower.replace(" pro", "")
        if f"iphone {numero}" not in titre_lower and f"iphone{numero}" not in titre_lower:
            return False
    else:
        numero = modele_lower
        if f"iphone {numero}" not in titre_lower and f"iphone{numero}" not in titre_lower:
            return False
        if "pro" in titre_lower:
            return False
    for mauvais in MODELES_INTERDITS:
        if mauvais in titre_lower:
            return False
    return True

def valider_prix(prix):
    if prix is None:
        return None
    try:
        if isinstance(prix, (int, float)):
            return float(prix)
        if isinstance(prix, str):
            prix_clean = re.sub(r'[^\d.,]', '', prix)
            prix_clean = prix_clean.replace(',', '.')
            return float(prix_clean)
    except:
        return None
    return None

def creer_session():
    session = requests.Session()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    ]
    session.headers.update({
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    return session

def scraper_via_api(session, recherche):
    try:
        session.get("https://www.vinted.fr", timeout=15)
        time.sleep(random.uniform(2, 4))
        params = {
            "search_text": recherche["mots_cles"],
            "price_from": recherche["prix_min"],
            "price_to": recherche["prix_max"],
            "order": "newest_first",
            "currency": "EUR",
            "per_page": 20
        }
        response = session.get("https://www.vinted.fr/api/v2/catalog/items", params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', []), "api"
        elif response.status_code == 403:
            return None, "blocked"
        else:
            return [], "error"
    except Exception as e:
        print(f"Erreur API: {e}")
        return [], "error"

def scraper_via_html(session, recherche):
    try:
        search_text = recherche["mots_cles"].replace(" ", "+")
        url = f"https://www.vinted.fr/catalog?search_text={search_text}&price_from={recherche['prix_min']}&price_to={recherche['prix_max']}&order=newest_first"
        session.get("https://www.vinted.fr", timeout=15)
        time.sleep(random.uniform(3, 5))
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        item_cards = soup.select('[data-testid="grid-item"], .feed-grid__item')
        for card in item_cards[:15]:
            try:
                link = card.find('a', href=True)
                if not link:
                    continue
                href = link.get('href', '')
                if '/items/' not in href:
                    continue
                match = re.search(r'/items/(\d+)', href)
                if not match:
                    continue
                item_id = match.group(1)
                title_elem = card.find('img', alt=True)
                titre = title_elem.get('alt', '') if title_elem else ''
                price_elem = card.find(string=re.compile(r'\d+[,.]?\d*'))
                prix = "??"
                if price_elem:
                    prix_match = re.search(r'(\d+[,.]?\d*)', price_elem)
                    if prix_match:
                        prix = prix_match.group(1).replace(',', '.')
                items.append({'id': item_id, 'title': titre, 'prix': prix, 'url': f"https://www.vinted.fr{href}"})
            except:
                continue
        return items
    except Exception as e:
        print(f"Erreur HTML: {e}")
        return []

def traiter_annonce(item, recherche, source="api"):
    global annonces_vues
    if source == "api":
        item_id = item.get('id')
        titre = item.get('title', '')
        description = item.get('description', '')
        prix_data = item.get('total_item_price', {})
        prix = prix_data.get('amount') if isinstance(prix_data, dict) else prix_data
        url = f"https://www.vinted.fr{item.get('path', '')}"
    else:
        item_id = item.get('id')
        titre = item.get('title', '')
        description = ''
        prix = item.get('prix', '??')
        url = item.get('url', '')

    if not item_id or item_id in annonces_vues:
        return False
    annonces_vues.add(item_id)

    prix_valide = valider_prix(prix)
    if prix_valide is None:
        return False

    if est_un_scam(titre, description):
        print(f"🚫 SCAM: {titre[:40]}...")
        return False

    if est_une_piece_ou_accessoire(titre):
        print(f"🔧 PIECE/ACCESSOIRE: {titre[:40]}...")
        return False

    if not verifier_modele(titre, recherche["modele"]):
        print(f"❌ MAUVAIS MODELE: {titre[:40]}...")
        return False

    msg = f"🔥 <b>{recherche['nom']} trouvé!</b>\n📱 {titre}\n💰 {prix_valide:.2f}€\n🔗 <a href='{url}'>VOIR SUR VINTED</a>"
    if envoyer_telegram(msg):
        print(f"✅ MATCH: {titre[:40]}...")
        return True
    return False

def scraper_vinted():
    session = creer_session()
    use_html_fallback = False
    for recherche in RECHERCHES:
        print(f"🔍 {recherche['nom']}")
        try:
            if not use_html_fallback:
                items, status = scraper_via_api(session, recherche)
                if status == "blocked":
                    use_html_fallback = True
                    items = scraper_via_html(session, recherche)
                    source = "html"
                elif items:
                    source = "api"
                else:
                    items = []
                    source = "api"
            else:
                items = scraper_via_html(session, recherche)
                source = "html"
            matches = 0
            for item in items[:15]:
                if traiter_annonce(item, recherche, source):
                    matches += 1
            print(f"   {len(items)} scannés, {matches} matchs")
            time.sleep(random.uniform(8, 15))
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)

def main():
    print("=" * 50)
    print("BOT VINTED - Anti-Scam V4")
    print("=" * 50)
    envoyer_telegram("🚀 Bot Vinted V4 démarré — filtres scam + pièces actifs!")
    cycle = 1
    while True:
        print(f"\n📦 CYCLE #{cycle}")
        scraper_vinted()
        print(f"Cycle #{cycle} terminé. Pause 2 min...")
        cycle += 1
        time.sleep(120)

if __name__ == "__main__":
    main()