import time
import requests

# --- CONFIGURATION TON BOT ---
TELEGRAM_TOKEN = "8774623526:AAG4IXZvcme1_5C_gLNGhvQNq3lLXV6ygQs"
CHAT_ID = "7853415869"

# --- FILTRES SONY XM4 ---
PRIX_MIN = 40   
PRIX_MAX = 85   

BLACKLIST = [
    "boite seule", "boite vide", "uniquement la boite", "packaging",
    "pour pièce", "pour pieces", "en panne", "hs", "ne fonctionne pas",
    "cassé", "casse", "fissuré", "un côté ne marche plus", "mousse à changer",
    "copie", "fausse", "faux", "replique", "réplique"
]

URL_VINTED = "https://www.vinted.fr/catalog?search_text=sony%20wh-1000xm4&status_ids[]=6&status_ids[]=1&status_ids[]=2&order=newest_first"

seen_ids = set()

def envoyer_notif(titre, prix, lien):
    message = (
        f"🎧 **SNARE / SONY XM4 DISPO !** 🎧\n\n"
        f"📌 {titre}\n"
        f"💰 Prix : {prix}€\n"
        f"🔗 [Clique ici pour l'acheter rapidement]({lien})"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erreur envoi Telegram : {e}")

def verifier_annonce(titre, description, prix):
    texte_a_verifier = (titre + " " + description).lower()
    
    if prix < PRIX_MIN or prix > PRIX_MAX:
        return False
        
    for mot in BLACKLIST:
        if mot in texte_a_verifier:
            return False
            
    return True
